import threading
import socket
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()
n = 0

# 违禁词列表
FORBIDDEN_WORDS = ["fuck", "sb", "shit" ]

# 过滤违禁词函数
def filter_message(message):
    for word in FORBIDDEN_WORDS:
        message = message.replace(word, "*" * len(word))
    return message

def start_server(log_area, status_label):
    global n
    def handle_client(conn, addr):
        global n
        n += 1
        log_area.insert(tk.END, f"[有新的连接] {addr}, 当前连接数 {n}\n")
        log_area.see(tk.END)
        try:
            while True:
                msg = conn.recv(1024).decode(FORMAT)
                if not msg or msg == DISCONNECT_MESSAGE:
                    break

                # 过滤违禁词
                filtered_msg = filter_message(msg)
                log_area.insert(tk.END, f"[{addr}] {filtered_msg}\n")
                log_area.see(tk.END)

                # 广播消息给所有客户端
                with clients_lock:
                    for c in clients:
                        c.sendall(f"[{addr}] {filtered_msg}".encode(FORMAT))
        finally:
            with clients_lock:
                clients.remove(conn)
            conn.close()
            n -= 1
            log_area.insert(tk.END, f"[断开连接] {addr}, 当前连接数 {n}\n")
            log_area.see(tk.END)

    def server_thread():
        server.listen()
        status_label.config(text="服务器运行中...")
        while True:
            try:
                conn, addr = server.accept()
                with clients_lock:
                    clients.add(conn)
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                log_area.insert(tk.END, f"[错误] {str(e)}\n")
                log_area.see(tk.END)
                break

    threading.Thread(target=server_thread, daemon=True).start()

def stop_server():
    global server
    server.close()

def create_server_gui():
    root = tk.Tk()
    root.title("服务器")
    
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    log_area = ScrolledText(frame, width=50, height=20)
    log_area.pack(padx=5, pady=5)

    status_label = tk.Label(frame, text="服务器未启动")
    status_label.pack(pady=5)

    start_button = tk.Button(frame, text="启动服务器", command=lambda: start_server(log_area, status_label))
    start_button.pack(side=tk.LEFT, padx=5)

    stop_button = tk.Button(frame, text="停止服务器", command=stop_server)
    stop_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

create_server_gui()
