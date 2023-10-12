import tkinter as tk
import time
def average_api_wait_time(self):
    self.menu_bar.delete(3)
    menubar
def repeat():
    time_end = time.time()
    delta = str(round(time_end - time_start, 2))
    print(delta)

    # Remove the existing "Edit" menu
    menu.delete(2)

    # Create a new "Edit" menu with the updated label
    editmenu = tk.Menu(menu, tearoff=0)
    menu.insert_cascade(2, label="Current Wait time " + delta, menu=editmenu)

    root.after(1000, repeat)

root = tk.Tk()
menu = tk.Menu(root)
root.config(menu=menu)

# Create a submenu
filemenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)

# Create an initial "Edit" menu
editmenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Edit", menu=editmenu)

# Initialize the time_start variable before calling repeat
time_start = time.time()

repeat()

root.mainloop()