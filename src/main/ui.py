import threading
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from brain import ChatbotBackend
from save_load import Database
from ttkthemes import ThemedStyle
import time
from PIL import ImageTk
import webbrowser


# Define a class to represent chat messages
class ChatMessage:
    def __init__(self, text, is_user=False):
        """
        Initializes a chat message.

        Args:
            text (str): The text of the message.
            is_user (bool): Whether the message is from the user (True) or bot (False).
        """
        self.text = text
        self.is_user = is_user


# Define a custom Entry widget with a placeholder text
class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        """
        Initializes an Entry widget with a placeholder text.

        Args:
            container: The parent container.
            placeholder (str): The placeholder text.
        """
        super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
        self.placeholder = placeholder
        self.insert("0", self.placeholder)


# Define the main Chatbot application class
class ChatbotApp:
    def __init__(self, data, icon):
        """
        Initializes the ChatbotApp.

        Args:
            data (dict): Configuration data for the chatbot.
        """

        if getattr(sys, "frozen", False):
            import pyi_splash

            pyi_splash.close()
        self.name = "ChameleonAI"
        self.data = data
        self.icon = icon
        self.db = Database(self.data)
        self.api_key = self.db.get_api()
        self.priming = self.db.get_priming()
        self.decorator = self.db.get_decorator()
        self.is_api_menu_open = False
        self.is_configure_menu_open = False
        self.api_menu_list = []
        self.configure_menu_list = []
        self.is_timeout = False
        self.average_api_wait_time = 0
        self.api_call_count = 0
        self.root = tk.Tk()
        self.root.title(self.name)
        self.root.attributes("-topmost", True)
        self.window_height = 300
        self.window_width = 500
        self.create_ui()
        self.setup_styles()
        self.root.after_idle(self.create_taskbar_icon)
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_window_closing)
        self.reset_chat()

    def create_taskbar_icon(self):
        icon = ImageTk.PhotoImage(self.icon)
        self.root.iconphoto(True, icon)

    def create_ui(self):
        # Create the application window, menus, chat frame, and input frame
        self.create_window()
        self.create_menu()
        self.create_chat_frame()
        self.create_input_frame()

    def create_window(self):
        """
        Create the application window and set its properties.
        """
        self.root.resizable(width=False, height=False)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def create_menu(self):
        """
        Create the application menu.
        """
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.configure_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_command(label="Personality", command=self.open_configure_menu)
        self.api_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_command(label="API", command=self.open_api_menu)
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_command(label='About', command=self.open_github)
        self.about_menu.config(fg = 'blue', cursor='hand2')
    def open_github(self):
        webbrowser.open("https://github.com/himisir")
    def open_link(self, event):
        webbrowser.open("https://makersuite.google.com/app/apikey")

    def display_average_api_wait_time(self, last_api_call_wait_time):
        """
        Displays the average API call wait time
        Conflicts with API set up menu, skipping it for now
        """

        return None
        try:
            self.menu_bar.delete(3)
        except:
            pass

        self.average_api_wait_time += last_api_call_wait_time
        average = self.average_api_wait_time // self.api_call_count
        self.average_api_wait_time_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(
            label="Average API Wait Time: " + str(average) + " sec"
        )

    def create_chat_frame(self):
        """
        Create the chat frame to display the conversation history.
        """
        self.chat_container = ttk.Frame(self.root)
        self.chat_container.pack(fill=tk.BOTH, expand=True)

        self.chat_history = tk.Text(
            self.chat_container,
            wrap="word",
            bg="#f5f5f5",
            state="disabled",
            bd=0,
            highlightthickness=0,
            padx=5,
            pady=5,
            spacing1=10,
            foreground="black",
            font=("Arial", 14),
        )
        self.chat_history.tag_configure(
            "user_tag", justify="right", background="#0084ff"
        )
        self.chat_history.tag_configure("bot_tag", justify="left", background="#e0e0e0")
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        self.chat_history.place(relheight=0.8, relwidth=1, relx=0)

    def create_input_frame(self):
        """
        Create the input frame for user messages and controls.
        """
        self.input_frame = ttk.Frame(self.chat_container)

        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.chat_reset_button = ttk.Button(
            self.input_frame,
            text="Reset",
            command=self.reset_chat,
            style="Reset.TButton",
        )
        self.chat_reset_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.user_input = ttk.Entry(
            self.input_frame, style="User.TEntry", font=("Arial", 14)
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
            style="Send.TButton",
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.input_frame.place(relheight=0.2, relwidth=1, rely=0.8)

    def setup_styles(self):
        """
        Setup styles and themes for the application.
        """
        themed_style = ThemedStyle(self.root)
        themed_style.set_theme("clam")
        self.root.style = ttk.Style()
        self.root.style.configure(
            "Reset.TButton", font=("Arial", 14), padding=(10, 5), relief=tk.RAISED
        )
        self.root.style.configure(
            "User.TEntry", font=("Arial", 14), padding=(10, 5), borderwidth=2
        )
        self.root.style.configure(
            "Send.TButton", font=("Arial", 14), padding=(10, 5), relief=tk.RAISED
        )

    def on_root_window_closing(self):
        """
        Handle the event when the application window is closed.
        """
        if messagebox.askokcancel(
            "Closing app", "Do you really want to close the app?"
        ):
            self.root.destroy()

    def send_message(self, event=None):
        """
        Send a user message to the chatbot when the user hits 'Enter'.
        """
        if len(self.api_key) < 5:
            self.open_api_menu()
            return None
        if self.is_api_menu_open or self.is_configure_menu_open:
            handle_widget_thread = threading.Thread(
                target=self.handle_widget_not_closed()
            )
            handle_widget_thread.start()
            return None
        if self.is_timeout:
            return None
        user_message = self.user_input.get()
        if user_message:
            self.user_input.delete(0, tk.END)
            self.display_message(f"You: {user_message}", is_user=True)
            bot_message_thread = threading.Thread(
                target=self.bot_message, args=(user_message,)
            )
            bot_message_thread.start()

    def bot_message(self, user_message):
        """
        Generate a bot response to a user message.
        """
        start_time = time.time()
        self.is_timeout = True
        wait_timer_thread = threading.Thread(
            target=self.wait_timer,
            args=[
                start_time,
                1,
            ],
        )
        wait_timer_thread.start()
        bot_response = self.chatbot_backend.generate_text(user_message)
        self.is_timeout = False
        # end_time = time.time()
        # self.api_call_count += 1
        # api_call_time_thread = threading.Thread(
        #     target=self.display_average_api_wait_time, args=(end_time - start_time,)
        # )
        # api_call_time_thread.start()
        # print("API wait time: ", end_time - start_time)
        self.display_message(f"Bot: {bot_response}", is_user=False)

    def remove_highlight(self):
        """
        Remove highlighting from chat history.
        """
        self.chat_history.tag_remove("highlight", "1.0", "end")

    def display_message(self, message, is_user=False):
        """
        Display a chat message in the chat history.

        Args:
            message (str): The message to display.
            is_user (bool): Whether the message is from the user (True) or bot (False).
        """
        chat_message = ChatMessage(message, is_user)
        self.render_message(chat_message)

    def render_message(self, chat_message):
        """
        Render a chat message in the chat history.

        Args:
            chat_message (ChatMessage): The chat message to render.
        """
        message_text = chat_message.text
        tag = "user_tag" if chat_message.is_user else "bot_tag"
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, f"{message_text}\n", tag)
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def open_configure_menu(self):
        """
        Open the configuration menu for the chatbot.
        """
        if self.is_configure_menu_open:
            self.configure_window.attributes("-topmost", True)
            return None

        self.configure_window = tk.Toplevel(self.root)
        configure_window = self.configure_window
        configure_window.attributes("-topmost", True)
        configure_window.title("Personality Settings")

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        configure_window.geometry("+%d+%d" % (x + 50, y + 50))

        priming_label = ttk.Label(configure_window, text="Character")
        priming_label.grid(row=0, column=0, padx=10, sticky="w")
        priming = "I am ChameleonAI"
        if len(self.priming) < 2:
            self.priming = priming
        priming_entry = PlaceholderEntry(configure_window, self.priming)
        priming_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        decorator_label = ttk.Label(configure_window, text="Personality")
        decorator_label.grid(row=2, column=0, padx=10, sticky="w")

        decorator = "I'm everything you've ever wanted!"
        if len(self.decorator) < 2:
            self.decorator = decorator
        decorator_entry = PlaceholderEntry(configure_window, self.decorator)
        decorator_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        save_button = ttk.Button(
            configure_window,
            text="Save",
            command=lambda: self.save_agent_configuration(
                priming_entry.get(), decorator_entry.get()
            ),
        )
        save_button.grid(row=4, column=1, padx=10, pady=10)

        self.is_configure_menu_open = True
        self.configure_menu_list.append(configure_window)
        configure_window.protocol("WM_DELETE_WINDOW", self.on_configure_menu_closing)
        configure_window.wait_window(configure_window)

    def open_api_menu(self):
        """
        Open the API key update menu.
        """
        if self.is_api_menu_open:
            self.api_window.attributes("-topmost", True)
            return None

        self.api_window = tk.Toplevel(self.root)
        api_window = self.api_window
        api_window.attributes("-topmost", True)
        api_window.title("Update API Key")

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        api_window.geometry("+%d+%d" % (x + 70, y + 50))

        if len(self.api_key) < 5:
            default_api_value = "PUT YOUR PALM API KEY HERE"
        else:
            default_api_value = self.api_key
        api_entry_var = default_api_value

        api_create_label = ttk.Label(api_window, text="GET API")
        api_create_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        api_create_link = tk.Label(
            api_window,
            fg="blue",
            cursor="hand2",
            font=("arial", 12, "italic"),
            text="https://makersuite.google.com/app/apikey",
        )
        api_create_link.bind("<Button-1>", self.open_link)
        api_create_link.grid(row=0, column=1, padx=5)

        api_key_label = ttk.Label(api_window, text="API KEY")
        api_key_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        api_key_entry = PlaceholderEntry(api_window, api_entry_var)
        api_key_entry.grid(row=1, column=1, padx=5, sticky="ew")

        save_button = ttk.Button(
            api_window,
            text="Update",
            command=lambda: self.save_api_configuration(api_key_entry.get()),
        )
        save_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.is_api_menu_open = True
        self.api_menu_list.append(api_window)
        api_window.protocol("WM_DELETE_WINDOW", self.on_api_menu_closing)
        api_window.wait_window(api_window)

    def on_configure_menu_closing(self):
        """
        Handle the event when the configuration menu is closed.
        """
        for widget in self.configure_menu_list:
            widget.destroy()
        self.is_configure_menu_open = False
        self.configure_menu_list.clear()

    def on_api_menu_closing(self):
        """
        Handle the event when the API key update menu is closed.
        """
        for widget in self.api_menu_list:
            widget.destroy()
        self.is_api_menu_open = False
        self.api_menu_list.clear()

    def save_agent_configuration(self, priming_text, decorator_text):
        """
        Save the agent's configuration settings.

        Args:
            priming_text (str): The new priming text.
            decorator_text (str): The new decorator text.
        """
        self.priming = priming_text
        self.decorator = decorator_text
        self.db.set_priming(self.priming)
        self.db.set_decorator(self.decorator)

        for widget in self.configure_menu_list:
            widget.destroy()
        self.is_configure_menu_open = False
        self.configure_menu_list.clear()

        reset_thread = threading.Thread(target=self.reset_chat)
        reset_thread.start()

    def save_api_configuration(self, api_key):
        """
        Save the updated API key.

        Args:
            api_key (str): The new API key.
        """
        self.api_key = api_key
        self.db.set_api(self.api_key)
        for widget in self.api_menu_list:
            widget.destroy()
        self.is_api_menu_open = False
        self.api_menu_list.clear()

        if len(self.api_key) < 10:
            self.open_api_menu()
            return None

        reset_thread = threading.Thread(target=self.reset_chat)
        reset_thread.start()

    def handle_widget_not_closed(self):
        messagebox.showwarning(
            title="Close menu!",
            message="Close API setup menu first"
            if self.is_api_menu_open
            else "Close Personality Settings menu first",
        )
        if self.is_configure_menu_open:
            self.configure_window.attributes("-topmost", True)
        if self.is_api_menu_open:
            self.api_window.attributes("-topmost", True)

    def reset_chat(self):
        """
        Reset the chat and initialize the chatbot.
        """
        if self.is_timeout:
            return None
        self.chatbot_backend = ChatbotBackend(self.api_key)
        bot_initialize_thread = threading.Thread(target=self.bot_initialize)
        bot_initialize_thread.start()

    def bot_initialize(self):
        """
        Initialize the chatbot with priming and decorator text.
        """

        if len(self.api_key) < 10:
            self.open_api_menu()
            return None

        if self.is_api_menu_open or self.is_configure_menu_open:
            handle_widget_thread = threading.Thread(
                target=self.handle_widget_not_closed()
            )
            handle_widget_thread.start()
            return None

        context = self.priming + self.decorator
        start_time = time.time()
        self.is_timeout = True
        wait_timer_thread = threading.Thread(
            target=self.wait_timer,
            args=[
                start_time,
                0,
            ],
        )
        wait_timer_thread.start()
        bot_response = self.chatbot_backend.initialize(context)
        self.is_timeout = False
        end_time = time.time()

        # self.api_call_count = 1
        # self.average_api_wait_time = 0
        # api_call_time_thread = threading.Thread(
        #     target=self.display_average_api_wait_time, args=(end_time - start_time,)
        # )
        # api_call_time_thread.start()

        print("API wait time: ", end_time - start_time)
        self.chat_history.configure(state="normal")
        self.chat_history.delete("1.0", "end")
        self.chat_history.configure(state="disabled")
        self.display_message(f"Bot: {bot_response}", is_user=False)

    def wait_timer(self, start_time, val):
        if val == 0:
            text = "Reset"
            button = self.chat_reset_button
        else:
            text = "Send"
            button = self.send_button

        while self.is_timeout:
            wait_time = round((time.time() - start_time), 2)
            button.config(text=str(wait_time))
            time.sleep(0.1)
        button.config(text=text)

    def run(self):
        """
        Run the application's main loop.
        """
        self.root.mainloop()
