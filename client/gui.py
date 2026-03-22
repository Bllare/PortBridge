import threading
import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkTextbox
import webbrowser
import time
import re
from .client import UDPProxy
from utils.placeholder import PlaceholderEntry


class UDPClientGUI:
    def __init__(self):
        self.proxy = None
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = CTk()
        self.root.title("Port Bridge")
        self.root.geometry("430x520")
        self.root.minsize(450, 450)  # Increased minimum size
        
        # Statistics tracking
        self.total_download = 0
        self.total_upload = 0
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
            text="🔁 Bridge Client",
            font=("Arial", 20, "bold"),
            text_color="#4db8ff"  # Light blue
        )
        title_label.pack(anchor="center")
        
        subtitle_label = CTkLabel(
            header_frame,
            text="Forward UDP traffic between endpoints",
            font=("Arial", 12),
            text_color="#ffffff"  # Bright cyan
        )
        subtitle_label.pack(anchor="center", pady=(5, 0))
        
        # Configuration Card
        config_frame = CTkFrame(main_container, corner_radius=8)
        config_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        
        # Local port
        local_frame = CTkFrame(config_frame, fg_color="transparent")
        local_frame.pack(fill="x", pady=(10, 5), padx=10)
        
        CTkLabel(
            local_frame,
            text="Local Port:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        self.local_port_var = ctk.StringVar(value="27015")
        local_port_entry = CTkEntry(
            local_frame,
            text_color="#ffffff",
            textvariable=self.local_port_var,
            width=100
        )
        local_port_entry.pack(side="left")
        
        CTkLabel(
            local_frame,
            text="(Listening on 0.0.0.0)",
            font=("Arial", 12),
            text_color="#00e1ff"  # Blue
        ).pack(side="left", padx=(10, 0))
        
        # Remote host
        remote_host_frame = CTkFrame(config_frame, fg_color="transparent")
        remote_host_frame.pack(fill="x", pady=5, padx=10)
        
        CTkLabel(
            remote_host_frame,
            text="Remote Host:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        # Use custom PlaceholderEntry instead of CTkEntry
        self.remote_host_entry = PlaceholderEntry(
            remote_host_frame,
            placeholder_text="10.0.0.1, example.ocm",
            placeholder_color="#a0a0a0",
            text_color="#ffffff",
            width=200
        )
        self.remote_host_entry.pack(side="left", fill="x", expand=True)
        
        # Remote port
        remote_port_frame = CTkFrame(config_frame, fg_color="transparent")
        remote_port_frame.pack(fill="x", pady=5, padx=10)
        
        CTkLabel(
            remote_port_frame,
            text="Remote Port:",
            font=("Arial", 12, "bold"),
            width=100,
            text_color="#ffffff"  # White
        ).pack(side="left", padx=(0, 10))
        
        # Use custom PlaceholderEntry instead of CTkEntry
        self.remote_port_entry = PlaceholderEntry(
            remote_port_frame,
            placeholder_text="1234",
            placeholder_color="#a0a0a0",
            text_color="#ffffff",
            width=100
        )
        self.remote_port_entry.pack(side="left", fill="x", expand=True)
        
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
            text="▶ Start Proxy",
            text_color="#ffffff",
            text_color_disabled="#afafaf",
            command=self.start_proxy,
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
            command=self.stop_proxy,
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
        

        # Upload stats
        self.upload_label = CTkLabel(
            stats_frame,
            text="▲: 0.0 KB/s | Total: 0.0 KB",
            font=("Arial", 9),
            text_color="#00ff00"  # Light blue
        )
        self.upload_label.pack(side="left", padx=(0, 10))

        # Download stats
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
                    elif "Server → Client" in message:
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
        
    def start_proxy(self):
        try:
            # Reset counters when starting
            self.total_download = 0
            self.total_upload = 0
            self.last_download = 0
            self.last_upload = 0
            self.last_update_time = time.time()
            
            local_port = int(self.local_port_var.get().strip())
            remote_host = self.remote_host_entry.get().strip()  # Get from custom entry
            remote_port_str = self.remote_port_entry.get().strip()  # Get from custom entry
            
            # Validate inputs
            if not remote_host:
                self.log_message("❌ Error: Remote host cannot be empty")
                return
                
            if not remote_port_str:
                self.log_message("❌ Error: Remote port cannot be empty")
                return
                
            remote_port = int(remote_port_str)
            
            if not (1 <= local_port <= 65535):
                self.log_message("❌ Error: Local port must be between 1 and 65535")
                return
                
            if not (1 <= remote_port <= 65535):
                self.log_message("❌ Error: Remote port must be between 1 and 65535")
                return
            
            # Create and start proxy
            self.proxy = UDPProxy(local_port, remote_host, remote_port, self.log_message)
            
            # Start proxy in separate thread
            self.proxy.thread = threading.Thread(target=self.proxy.start, daemon=True)
            self.proxy.thread.start()
            
            # Update UI
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Update status indicators
            self.short_status_label.configure(text="Running", text_color="#4CAF50")
            self.status_indicator.configure(text_color="#4CAF50")
            self.status_label.configure(
                text=f"0.0.0.0:{local_port} → {remote_host}:{remote_port}"
            )
            
            # Log startup
            self.log_message("=" * 20)
            self.log_message("🚀 UDP Proxy started successfully!")
            self.log_message(f"📍 Local: 127.0.0.1:{local_port}")
            self.log_message(f"🌐 Remote: {remote_host}:{remote_port}")
            self.log_message("=" * 20)
            
        except ValueError as e:
            self.log_message(f"❌ Invalid port number: {e}")
        except Exception as e:
            self.log_message(f"❌ Failed to start proxy: {e}")
            
    def stop_proxy(self):
        if self.proxy:
            self.proxy.stop()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_indicator.configure(text_color="#F44336")
            self.short_status_label.configure(text="Stopped", text_color="#FFFFFF")
            self.status_label.configure(text="")
            self.log_message("🛑 Proxy stopped by user")
            
    def run(self):
        self.root.mainloop()