# 示例：Python中使用socket发送多播数据

import socket
import struct

# 设置多播地址和端口
MCAST_GRP = '224.0.0.1'
MCAST_PORT = 5007

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 设置为多播发送
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

# 发送数据
message = b'Hello, Multicast'
sock.sendto(message, (MCAST_GRP, MCAST_PORT))

sock.close()
