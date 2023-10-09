import threading
import tkinter as tk
from tkinter import ttk
from brain import ChatbotBackend
from save_load import Database
from ttkthemes import ThemedStyle

class ChatMessage:
    def __init__(self, text, is_user=False):
        self.text = text
        self.is_user = is_user

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
        self.placeholder = placeholder
        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
    def _clear_placeholder(self, e):
        if self["style"] == "Placeholder.TEntry":
            self.delete("0", "end")
            self["style"] = "TEntry"
    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = "Placeholder.TEntry"
    

class ChatbotApp:
    def __init__(self, data):
        self.name = 'Assistant'
        self.data = data
        self.db = Database(self.data)
        self.api_key = self.db.get_api()
        self.priming = self.db.get_priming()
        self.decorator = self.db.get_decorator()
        self.chatbot_backend = ChatbotBackend(self.api_key)
        self.root = tk.Tk()
        self.root.title(self.name)
        self.create_ui()
        self.setup_styles()
        self.reset_chat()

    def create_ui(self):
        self.create_menu()
        self.create_chat_frame()
        self.create_input_frame()

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.configure_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_command(
            label="Purpose", command=self.open_configure_menu)
        self.api_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_command(
            label="API", command=self.open_api_menu)
        

    def create_chat_frame(self):
        self.chat_container = ttk.Frame(self.root)
        self.chat_container.pack(fill=tk.BOTH, expand=True)

        # Chat history
        self.chat_history = tk.Text(self.chat_container, wrap="word", bg="#f5f5f5", state="disabled",
                                    bd=0, highlightthickness=0, spacing1=10, foreground="black", font=("Arial", 14))
        self.chat_history.tag_configure(
            "user_tag", justify="right", background="#0084ff")
        self.chat_history.tag_configure(
            "bot_tag", justify="left", background="#e0e0e0")
        self.chat_history.pack(fill=tk.BOTH, expand=True)

    def create_input_frame(self):
        # Input frame
        self.input_frame = ttk.Frame(self.chat_container)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.chat_reset_button = ttk.Button(
            self.input_frame, text="Reset", command=self.reset_chat, style="Reset.TButton")
        self.chat_reset_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.user_input = ttk.Entry(
            self.input_frame, style="User.TEntry", font=("Arial", 14))
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(
            self.input_frame, text="Send", command=self.send_message, style="Send.TButton")
        self.send_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_styles(self):
        themed_style = ThemedStyle(self.root)
        themed_style.set_theme("adapta")
        self.root.style = ttk.Style()
        self.root.style.configure("Reset.TButton", font=(
            "Arial", 14), padding=(10, 5), relief=tk.RAISED)
        self.root.style.configure("User.TEntry", font=(
            "Arial", 14), padding=(10, 5), borderwidth=2)
        self.root.style.configure("Send.TButton", font=(
            "Arial", 14), padding=(10, 5), relief=tk.RAISED)

    def send_message(self, event=None):
        user_message = self.user_input.get()
        if user_message:
            self.user_input.delete(0, tk.END)
            self.display_message(f'You: {user_message}', is_user=True)
            bot_message_thread = threading.Thread(target=self.bot_message, args=(user_message,))
            bot_message_thread.start()

    def bot_message(self, user_message):
            bot_response = self.chatbot_backend.generate_text(user_message)
            self.display_message(f'Bot: {bot_response}', is_user=False)
            self.chat_history.tag_add("highlight", "end-2l", "end")
            self.chat_history.after(500, self.remove_highlight)
        
    def remove_highlight(self):
        self.chat_history.tag_remove("highlight", "1.0", "end")

    def display_message(self, message, is_user=False):
        chat_message = ChatMessage(message, is_user)
        self.render_message(chat_message)

    def render_message(self, chat_message):
        message_text = chat_message.text
        tag = "user_tag" if chat_message.is_user else "bot_tag"
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, f"{message_text}\n", tag)
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def open_configure_menu(self):
        configure_window = tk.Toplevel(self.root)
        configure_window.title("Configure Agent")

        priming_label = ttk.Label(configure_window, text="Goal: 'You are a banana' for example!")
        priming_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        priming_entry= PlaceholderEntry(configure_window, self.priming)

        priming_entry.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        decorator_label = ttk.Label(configure_window, text="Guide: 'You make everything yellow' for example!")
        decorator_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        decorator_entry = PlaceholderEntry(configure_window, self.decorator)
        decorator_entry.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        save_button = ttk.Button(
            configure_window, text="Save", command=lambda: self.save_agent_configuration(priming_entry.get(), decorator_entry.get()))
        save_button.grid(row=4, column=1, padx=10, pady=10)
    
    def open_api_menu(self):
        api_window = tk.Toplevel(self.root)
        api_window.title("Update API Key")
        
        if self.api_key is None:
            default_api_value = "PUT YOUR PALM API KEY HERE"
        else:
            default_api_value = self.api_key
        api_entry_var = default_api_value
        
        api_key_label = ttk.Label(api_window, text="PaLM API Key:")
        api_key_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        api_key_entry = PlaceholderEntry(api_window, api_entry_var)
        
        api_key_entry.grid(row=0, column=1, padx=10, pady=5)        
        save_button = ttk.Button(
            api_window, text="Update", command=lambda: self.save_api_configuration(api_key_entry.get()))
        save_button.grid(row=1, column=1, padx=10, pady=10)

        
    def save_agent_configuration(self, priming_text, decorator_text):
        self.priming = priming_text
        self.decorator = decorator_text
        self.db.set_priming(self.priming)
        self.db.set_decorator(self.decorator)
        reset_thread = threading.Thread(target=self.reset_chat)
        reset_thread.start()
        
    def save_api_configuration(self, api_key):
        self.api_key = api_key
        self.db.set_api(self.api_key)
        
    def reset_chat(self):
        self.chatbot_backend = ChatbotBackend(self.api_key)
        bot_initialize_thread = threading.Thread(target=self.bot_initialize)
        bot_initialize_thread.start()

    def bot_initialize(self):
        context = self.priming + self.decorator
        prompt =  "You are " + context + " now tell us about you based on the information provided, in just one line, start with 'I am'"
        bot_response = self.chatbot_backend.initialize(
            context,prompt)
        self.chat_history.configure(state="normal")
        self.chat_history.delete("1.0", "end")
        self.chat_history.configure(state="disabled")
        self.display_message(f'Bot: {bot_response}', is_user=False)
        self.chat_history.tag_add("highlight", "end-2l", "end")
        self.chat_history.after(500, self.remove_highlight)
        
    def run(self):
        self.root.mainloop()