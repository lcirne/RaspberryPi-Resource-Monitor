from tkinter import *
import json
import socket

HOSTNAME = socket.gethostname()

# Initialize window
root = Tk()
root.title(f"{HOSTNAME}'s Resource Monitor")
root.geometry("350x500")

# Configure grid
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Window title frame
window_label_frame = Frame(
    root,
    bg='grey', #background color
    bd=2, #border width
    relief='solid',
)
window_label_frame.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
window_label = Label(
    window_label_frame, 
    text="Luke's MB-Air Resouece Monitor",
    bg="lightblue", 
    fg="black", 
    padx=0, 
    pady=0
)
window_label.grid(row=0, column=0, padx=0, pady=0)
#title_label = Label(
#    root, 
#    text='Macbook-A#ir Resource Monitor', 
#    relief=SOLID,
#    borderwidth=2
#)
#title_label.grid(ro#w=0, column=0, sticky='nw', padx=0, pady=0)

# Stop button
stop_button = Button(root, text='stop', width=6, command=root.destroy)
stop_button.grid(row=0, column=1, sticky='ne', padx=0, pady=0)
root.mainloop()
