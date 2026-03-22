import threading
import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkTextbox
import webbrowser
import time
import re
from .server import UDPRelay  # Import our restructured relay class
from utils.placeholder import PlaceholderEntry


class UDPRelayGUI:
    def __init__(self):
        self.relay = None
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = CTk()
        self.root.title("Port Relay")
        self.root.geometry("430x520")
        self.root.minsize(450, 450)  # Increased minimum size
        
        # Statistics tracking
        self.total_download = 0  # Server → Clients
        self.total_upload = 0    # Clients → Server
        self.last_download = 0
        self.last_upload = 0
        self.last_update_time = time.time()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with grid layout
        main_container = CTkFrame(self.root, corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid layout weights
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=0)  # Header
        main_container.grid_rowconfigure(1, weight=0)  # Config
        main_container.grid_rowconfigure(2, weight=1)  # Log area
        main_container.grid_rowconfigure(3, weight=0)  # Footer

        # Header with vibrant colors
        header_frame = CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        title_label = CTkLabel(
            header_frame,
            text="🔁 Relay Server",
            font=("Arial", 20, "bold"),
            text_color="#4db8ff"  # Light blue
        )
        title_label.pack(anchor="center")
        
        subtitle_label = CTkLabel(
            header_frame,
            text="Forward UDP traffic from multiple clients to a target server",
            font=("Arial", 12),
            text_color="#ffffff"  # Bright cyan
        )
        subtitle_label.pack(anchor="center", pady=(5, 0))
        
        # Configuration Card
        config_frame = CTkFrame(main_container, corner_radius=8)
        config_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        
        # Listen port
        listen_frame = CTkFrame(config_frame, fg_color="transparent")
        listen_frame.pack(fill="x", pady=(10, 5), padx=10)
        
        CTkLabel(
            listen_frame,
            text="Listen Port:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        # Use custom PlaceholderEntry instead of CTkEntry
        self.listen_port_entry = PlaceholderEntry(
            listen_frame,
            placeholder_text="1234",
            placeholder_color="#a0a0a0",
            text_color="#ffffff",
            width=100
        )
        self.listen_port_entry.pack(side="left")
        
        CTkLabel(
            listen_frame,
            text="(Listening on 0.0.0.0)",
            font=("Arial", 12),
            text_color="#00e1ff"  # Blue
        ).pack(side="left", padx=(10, 0))
        
        # Target host
        target_host_frame = CTkFrame(config_frame, fg_color="transparent")
        target_host_frame.pack(fill="x", pady=5, padx=10)
        
        CTkLabel(
            target_host_frame,
            text="Target Host:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        # Use normal CTkEntry with default value
        self.target_host_var = ctk.StringVar(value="127.0.0.1")
        self.target_host_entry = CTkEntry(
            target_host_frame,
            text_color="#ffffff",
            textvariable=self.target_host_var,
            width=200
        )
        self.target_host_entry.pack(side="left", fill="x", expand=True)
        
        # Target port
        target_port_frame = CTkFrame(config_frame, fg_color="transparent")
        target_port_frame.pack(fill="x", pady=5, padx=10)
        
        CTkLabel(
            target_port_frame,
            text="Target Port:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        # Use custom PlaceholderEntry instead of CTkEntry
        self.target_port_entry = PlaceholderEntry(
            target_port_frame,
            placeholder_text="27015",
            placeholder_color="#a0a0a0",
            text_color="#ffffff",
            width=100
        )
        self.target_port_entry.pack(side="left", fill="x", expand=True)
        
        # Control buttons
        button_frame = CTkFrame(config_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(15, 10), padx=10)
        
        # Status indicator
        self.status_indicator = CTkLabel(
            button_frame,
            text="●",
            font=("Arial", 16),
            text_color="#f44336",  # Red
            width=30
        )
        self.status_indicator.pack(side="left", padx=(0, 10))
        
        self.short_status_label = CTkLabel(
            button_frame,
            text="Ready",
            font=("Arial", 12),
            text_color="#ffffff"  # White
        )
        self.short_status_label.pack(side="left", padx=(0, 20))
        
        self.start_button = CTkButton(
            button_frame,
            text="▶ Start Relay",
            text_color="#ffffff",
            text_color_disabled="#afafaf",
            command=self.start_relay,
            fg_color="#4CAF50",  # Green
            hover_color="#388E3C",
            width=120
        )
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = CTkButton(
            button_frame,
            text="⏹ Stop",
            text_color="#ffffff",
            text_color_disabled="#afafaf",
            command=self.stop_relay,
            fg_color="#F44336",  # Red
            hover_color="#D32F2F",
            width=100,
            state="disabled"
        )
        self.stop_button.pack(side="left")
        
        # Status display
        status_frame = CTkFrame(config_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        self.status_label = CTkLabel(
            status_frame,
            text="",
            font=("Arial", 10),
            text_color="#4db8ff"  # Light blue
        )
        self.status_label.pack(fill="x")
        
        # Log area
        log_frame = CTkFrame(main_container, corner_radius=8)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        CTkLabel(
            log_frame,
            text="Activity Log",
            font=("Arial", 12, "bold"),
            corner_radius=8,
            text_color="#ffffff"  # White
        ).pack(fill="x", padx=10, pady=(10, 5))
        
        self.log_text = CTkTextbox(
            log_frame,
            font=("Consolas", 11),
            fg_color="#1e1e1e",
            text_color="#e0e0e0",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Fixed footer
        footer_frame = CTkFrame(main_container, fg_color="transparent", height=30)
        footer_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Stats section
        stats_frame = CTkFrame(footer_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 5))
        

        # Upload stats (clients → server)
        self.upload_label = CTkLabel(
            stats_frame,
            text="▲: 0.0 KB/s | Total: 0.0 KB",
            font=("Arial", 9),
            text_color="#00ff00"  # Light blue
        )
        self.upload_label.pack(side="left", padx=(0, 10))

        # Download stats (server → clients)
        self.download_label = CTkLabel(
            stats_frame,
            text="▼: 0.0 KB/s | Total: 0.0 KB",
            font=("Arial", 9),
            text_color="#ffa600"  # Light blue
        )
        self.download_label.pack(side="left")
        
        # Separator
        separator = CTkFrame(footer_frame, height=1, fg_color="#2b2b2b")
        separator.pack(fill="x", pady=(0, 5))
        
        # Footer content in a fixed frame
        footer_content = CTkFrame(footer_frame, fg_color="transparent", height=20)
        footer_content.pack(fill="x", pady=(0, 0))
        
        about_label = CTkLabel(
            footer_content,
            text="Made by Blare • GitHub: ",
            font=("Arial", 9),
            text_color="#b0b0b0",  # Light gray
            wraplength=150  # Wrap text if too narrow
        )
        about_label.pack(side="left")
        
        github_link = CTkLabel(
            footer_content,
            text="github.com/Bllare",
            font=("Arial", 9, "underline"),
            text_color="#4db8ff",  # Light blue
            cursor="hand2"
        )
        github_link.pack(side="left")
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Bllare"))
        
        version_label = CTkLabel(
            footer_content,
            text="• v1.0",
            font=("Arial", 9),
            text_color="#b0b0b0"  # Light gray
        )
        version_label.pack(side="right")
        
        # Start stats update timer
        self.root.after(1000, self.update_stats)
        
    def log_message(self, message):
        # Color coding
        if "started" in message.lower():
            color = "#4CAF50"  # Green
        elif "timeout" in message.lower():
            color = "#FF9800"  # Amber
        elif "error" in message.lower() or "failed" in message.lower():
            color = "#F44336"  # Red
        elif "stopped" in message.lower():
            color = "#FF9800"  # Amber
        else:
            color = "#00BCD4"  # Cyan
            
        self.log_text.insert("end", message + "\n")
        self.log_text.tag_add("colored", "end-2c linestart", "end-1c")
        self.log_text.tag_config("colored", foreground=color)
        self.log_text.see("end")
        
        # Parse byte counts from log messages
        if "bytes" in message:
            try:
                bytes_match = re.search(r'(\d+)\s*bytes', message)
                if bytes_match:
                    bytes_count = int(bytes_match.group(1))
                    if "Client → Server" in message:
                        self.total_upload += bytes_count
                    elif "Server → Clients" in message:
                        self.total_download += bytes_count
            except:
                pass
        
    def update_stats(self):
        now = time.time()
        elapsed = now - self.last_update_time

        # Calculate speeds in KB/s
        download_speed = (self.total_download - self.last_download) / elapsed / 1024
        upload_speed = (self.total_upload - self.last_upload) / elapsed / 1024

        # Update labels
        self.download_label.configure(text=f"▼: {download_speed:.1f} KB/s | Total: {self.total_download/1024:.1f} KB")
        self.upload_label.configure(text=f"▲: {upload_speed:.1f} KB/s | Total: {self.total_upload/1024:.1f} KB")

        # Reset counters
        self.last_download = self.total_download
        self.last_upload = self.total_upload
        self.last_update_time = now

        # Schedule next update
        self.root.after(1000, self.update_stats)
        
    def start_relay(self):
        try:
            # Reset counters when starting
            self.total_download = 0
            self.total_upload = 0
            self.last_download = 0
            self.last_upload = 0
            self.last_update_time = time.time()
            
            # Get listen port from entry
            listen_port_str = self.listen_port_entry.get().strip()
            if not listen_port_str:
                self.log_message("❌ Error: Listen port cannot be empty")
                return
            listen_port = int(listen_port_str)
            
            # Get target host and port
            target_host = self.target_host_var.get().strip()
            target_port_str = self.target_port_entry.get().strip()
            
            # Validate inputs
            if not target_host:
                self.log_message("❌ Error: Target host cannot be empty")
                return
                
            if not target_port_str:
                self.log_message("❌ Error: Target port cannot be empty")
                return
                
            target_port = int(target_port_str)
            
            if not (1 <= listen_port <= 65535):
                self.log_message("❌ Error: Listen port must be between 1 and 65535")
                return
                
            if not (1 <= target_port <= 65535):
                self.log_message("❌ Error: Target port must be between 1 and 65535")
                return
            
            # Create and start relay
            self.relay = UDPRelay(
                listen_host="0.0.0.0",
                listen_port=listen_port,
                target_host=target_host,
                target_port=target_port,
                log_callback=self.log_message
            )
            
            # Start relay in separate thread
            threading.Thread(target=self.relay.start, daemon=True).start()
            
            # Update UI
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Update status indicators
            self.short_status_label.configure(text="Running", text_color="#4CAF50")
            self.status_indicator.configure(text_color="#4CAF50")
            self.status_label.configure(
                text=f"0.0.0.0:{listen_port} → {target_host}:{target_port}"
            )
            
            # Log startup
            self.log_message("=" * 20)
            self.log_message("🚀 UDP Relay started successfully!")
            self.log_message(f"👂 Listening: 0.0.0.0:{listen_port}")
            self.log_message(f"🎯 Target: {target_host}:{target_port}")
            self.log_message("=" * 20)
            
        except ValueError as e:
            self.log_message(f"❌ Invalid port number: {e}")
        except Exception as e:
            self.log_message(f"❌ Failed to start relay: {e}")
            
    def stop_relay(self):
        if self.relay:
            self.relay.stop()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_indicator.configure(text_color="#F44336")
            self.short_status_label.configure(text="Stopped", text_color="#FFFFFF")
            self.status_label.configure(text="")
            self.log_message("🛑 Relay stopped by user")
            
    def run(self):
        self.root.mainloop()

def main():
    app = UDPRelayGUI()
    app.run()

if __name__ == "__main__":
    main()
