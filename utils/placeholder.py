import threading
import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkTextbox
import webbrowser
import time
import re

class PlaceholderEntry(CTkEntry):
    def __init__(self, *args, placeholder_text="", placeholder_color="#a0a0a0", **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder_text
        self.placeholder_color = placeholder_color
        self.default_fg_color = self._text_color
        self.is_placeholder_active = True  # Track placeholder state
        
        # Bind focus events
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
        # Bind key events to detect user input
        self.bind("<Key>", self.on_key_press)
        
        # Immediately show placeholder text
        self.configure(text_color=self.placeholder_color)
        super().insert(0, self.placeholder)
    
    def show_placeholder(self):
        if not super().get() and not self.is_placeholder_active:
            self.is_placeholder_active = True
            self.configure(text_color=self.placeholder_color)
            super().insert(0, self.placeholder)
    
    def on_focus_in(self, event):
        if self.is_placeholder_active:
            self.configure(text_color=self.default_fg_color)
            self.delete(0, 'end')
            self.is_placeholder_active = False
    
    def on_focus_out(self, event):
        if not super().get():
            self.show_placeholder()
    
    def on_key_press(self, event):
        # If placeholder is active and user types, remove placeholder
        if self.is_placeholder_active:
            self.configure(text_color=self.default_fg_color)
            self.delete(0, 'end')
            self.is_placeholder_active = False
    
    def get(self):
        if self.is_placeholder_active:
            return ""
        return super().get()