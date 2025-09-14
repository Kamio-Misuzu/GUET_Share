import random
import time
import threading

# 定义接收方的缓冲区大小
class Receiver:
    def __init__(self, initial_window_size=64):
        self.window_size = initial_window_size  # 初始窗口大小，单位KB
        self.buffer = 0  # 当前缓冲区已使用大小
        self.max_buffer = 128  # 最大缓冲区大小
        self.min_buffer = 32   # 最小缓冲区大小
    
    def update_window_size(self):
        """根据接收方的缓冲区状态动态调整窗口大小"""
        if self.buffer < 32:
            self.window_size = 32
        elif self.buffer > 100:
            self.window_size = 128
        else:
            self.window_size = 64
        print(f"接收方窗口大小调整为: {self.window_size}KB")
    
    def receive_data(self, data_size):
        """接收数据并更新缓冲区大小"""
        if self.buffer + data_size <= self.max_buffer:
            self.buffer += data_size
            print(f"接收方接收到 {data_size}KB 数据，当前缓冲区大小：{self.buffer}KB")
        else:
            print(f"接收方缓冲区已满，当前缓冲区大小：{self.buffer}KB，不能接收更多数据")
    
    def free_space(self):
        """返回剩余空间"""
        return self.max_buffer - self.buffer

# 定义发送方，控制发送的数据量
class Sender:
    def __init__(self, receiver):
        self.receiver = receiver

    def send_data(self):
        """发送数据并根据接收方的窗口调整发送量"""
        while True:
            # 获取当前接收方的窗口大小
            window_size = self.receiver.window_size
            
            # 模拟发送数据
            data_to_send = random.randint(1, window_size)
            
            if data_to_send <= self.receiver.free_space():
                # 如果接收方有足够的空间接收数据，则发送数据
                self.receiver.receive_data(data_to_send)
                print(f"发送方发送 {data_to_send}KB 数据")
            else:
                print(f"发送方等待，接收方缓冲区已满，最大可接收 {self.receiver.free_space()}KB 数据")
            
            # 根据接收方的缓冲区状态更新窗口大小
            self.receiver.update_window_size()
            time.sleep(1)

# 创建接收方对象
receiver = Receiver()

# 创建发送方对象
sender = Sender(receiver)

# 启动发送方线程
sender_thread = threading.Thread(target=sender.send_data)
sender_thread.daemon = True
sender_thread.start()

# 模拟接收方的缓冲区动态变化
for _ in range(10):
    # 模拟缓冲区的波动，接收方的缓冲区会随机增大或减小
    receiver.buffer += random.randint(-10, 20)
    receiver.buffer = max(0, min(receiver.buffer, receiver.max_buffer))  # 确保缓冲区大小在合法范围内
    time.sleep(2)

# 让主线程等待发送方工作
time.sleep(30)
