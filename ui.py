import tkinter as tk
from tkinter import ttk
from brain import ChatbotBackend
from ttkthemes import ThemedStyle

class ChatMessage:
    def __init__(self, text, is_user=False):
        self.text = text
        self.is_user = is_user

class ChatbotApp:
    def __init__(self, palm_api_key):
        self.name = 'Assistant'
        self.priming = 'You are a virtual chat bot, you are here to help the user with all of their questions.'
        self.decorator = 'Ask questions if you dont know the answer'
        self.chatbot_backend = ChatbotBackend(palm_api_key)
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
            label="Configure", command=self.open_configure_menu)

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
        themed_style.set_theme("plastik")
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
        configure_window.title("Configure")

        priming_label = ttk.Label(configure_window, text="Priming:")
        priming_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        priming_entry = ttk.Entry(configure_window, font=("Arial", 14))
        priming_entry.grid(row=0, column=1, padx=10, pady=5)

        decorator_label = ttk.Label(configure_window, text="Decorator:")
        decorator_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        decorator_entry = ttk.Entry(configure_window, font=("Arial", 14))
        decorator_entry.grid(row=1, column=1, padx=10, pady=5)

        save_button = ttk.Button(
            configure_window, text="Save", command=lambda: self.save_configuration(priming_entry.get(), decorator_entry.get()))
        save_button.grid(row=2, column=1, padx=10, pady=10)

    def save_configuration(self, priming_text, decorator_text):
        self.priming = priming_text
        self.decorator = decorator_text
        self.reset_chat()

    def reset_chat(self):
        self.chat_history.configure(state="normal")
        self.chat_history.delete("1.0", "end")
        self.chat_history.configure(state="disabled")

        context = self.priming + self.decorator
        bot_response = self.chatbot_backend.initialize(
            context, "You are " + context + " now tell us about you based on the information provided, in just one line, start with 'I am'")

        self.display_message(f'Bot: {bot_response}', is_user=False)
        self.chat_history.tag_add("highlight", "end-2l", "end")
        self.chat_history.after(500, self.remove_highlight)

    def run(self):
        self.root.mainloop()