import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import socket
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

client = None



def show_info():
    messagebox.showinfo("请输入文本信息")

def show_warning():
    messagebox.showwarning("未连接服务器...")

def connect_to_server(log_area, status_label):
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        status_label.config(text="已连接服务器")
        threading.Thread(target=receive_messages, args=(log_area,), daemon=True).start()
    except:
        log_area.insert(tk.END, "连接服务器失败\n")

def disconnect_from_server(status_label):
    global client
    if client:
        client.send(DISCONNECT_MESSAGE.encode(FORMAT))
        client.close()
        client = None
        status_label.config(text="未连接服务器")

def send_message(entry, log_area):
    global client
    msg = entry.get()
    
    if client and msg:
        client.send(msg.encode(FORMAT))
        log_area.insert(tk.END, f"你: {msg}\n")
        log_area.see(tk.END)
        entry.delete(0, tk.END)
    
    elif not msg and client:
        root = tk.Tk()
        tk.Message(root, text="请输入文本信息")
        # btn_info=tk.Message(root, text="请输入文本信息")
        # btn_info.pack(pady=5)
    else:
        root = tk.Tk()
        tk.Message(root, text="未连接服务器...")
        # btn_warning.pack(pady=5)
        



def receive_messages(log_area):
    global client
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                log_area.insert(tk.END, f"{msg}\n")
                log_area.see(tk.END)
        except:
            break

def create_client_gui():
    root = tk.Tk()
    root.title("客户端")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    log_area = ScrolledText(frame, width=50, height=20)
    log_area.pack(padx=5, pady=5)

    entry = tk.Entry(frame, width=40)
    entry.pack(side=tk.LEFT, padx=5, pady=5)

    send_button = tk.Button(frame, text="发送", command=lambda: send_message(entry, log_area))
    send_button.pack(side=tk.LEFT, padx=5)

    connect_button = tk.Button(frame, text="连接服务器", command=lambda: connect_to_server(log_area, status_label))
    connect_button.pack(side=tk.LEFT, padx=5)

    disconnect_button = tk.Button(frame, text="断开连接", command=lambda: disconnect_from_server(status_label))
    disconnect_button.pack(side=tk.LEFT, padx=5)

    status_label = tk.Label(frame, text="未连接服务器")
    status_label.pack(pady=5)

    root.mainloop()

create_client_gui()
