import subprocess

# 定义需要执行的命令
commands = [
    "ipconfig",                       # (1) 检查 TCP/IP 设置
    "ping zenzizn.cn",            # (2) 测试网络连通性
    "netstat -an",                    # (3) 显示 TCP/IP 网络连接情况
    "nslookup zenzizn.cn",        # (4) 查看 DNS 解析
    "tracert zenzizn.cn",         # (5) 路由跟踪
    "arp -a"                          # (6) 查看 ARP 缓存
]

# 执行每个命令并输出结果
for command in commands:
    print(f"\nExecuting: {command}")
    try:
        # 使用subprocess运行外部命令
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            # 运行时候结果报错, 即输出错误信息
            print(f"Errors:\n{result.stderr}")
    except Exception as e:
        # 如果不能运行, 说明不能运行的原因
        print(f"Error executing '{command}': {e}")
