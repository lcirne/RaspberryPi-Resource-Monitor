from tkinter import *
import json
import socket
from PIL import Image, ImageTk

HOSTNAME = socket.gethostname()

# Initialize window
root = Tk()
root.title(f"{HOSTNAME}'s Resource Monitor")
root.geometry("650x400")

# Configure grid
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=5)
root.grid_rowconfigure(2, weight=5)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Window title frame
window_label_frame = Frame(
    root,
    bg='lightgrey', #background color
    bd=2, #border width
    relief='solid',
)
window_label_frame.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
window_label = Label(
    window_label_frame, 
    text="Luke's MB-Air Resource Monitor",
    bg="lightblue", 
    fg="black", 
    padx=0, 
    pady=0
)
window_label.grid(row=0, column=0, padx=0, pady=0)


# CPU percentage usage graph
cpu_usage_frame = Frame(
    root,
    bg='grey',
    relief='solid',
    borderwidth=2
)
cpu_usage_frame.grid(row=1, column=0, sticky='n', padx=5, pady=5)
try:
    cpu_image_filepath = 'resource_graphs/test-cpu-graph.png'
    pil_cpu_image = Image.open(cpu_image_filepath)
    pil_cpu_image = pil_cpu_image.resize((250,187), Image.Resampling.LANCZOS)
    tk_cpu_image = ImageTk.PhotoImage(pil_cpu_image)
except FileNotFoundError:
    print(f'{cpu_image_filepath} not found.')
    root.destroy()

if tk_cpu_image:
    cpu_usage_label = Label(cpu_usage_frame, image=tk_cpu_image)
    cpu_usage_label.grid(row=1, column=0, padx=0, pady=0)


# Memory usage
mem_usage_frame = Frame(
    root,
    bg='grey',
    relief='solid',
    borderwidth=2
)
mem_usage_frame.grid(row=1, column=1, sticky='n', padx=5, pady=5)
try:
    mem_image_filepath = 'resource_graphs/test-mem-graph.png'
    pil_mem_image = Image.open(mem_image_filepath)
    pil_mem_image = pil_mem_image.resize((250, 187), Image.Resampling.LANCZOS)
    tk_mem_image = ImageTk.PhotoImage(pil_mem_image)
except FileNotFoundError:
    print(f'{mem_image_filepath} not found.')
    root.destroy()

if tk_mem_image:
    mem_usage_label = Label(mem_usage_frame, image=tk_mem_image)
    mem_usage_label.grid(row=1, column=1, padx=0, pady=0)


# Stop button
stop_button = Button(root, text='stop', width=6, command=root.destroy)
stop_button.grid(row=0, column=1, sticky='ne', padx=0, pady=0)
root.mainloop()
