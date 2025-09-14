class RouterNode:
    def __init__(self, destination, subnet_mask, next_hop, metric):
        self.destination = destination  # 网络地址 (IP 地址)
        self.subnet_mask = subnet_mask  # 子网掩码
        self.next_hop = next_hop        # 下一跳地址
        self.metric = metric            # 路由的度量值
        self.left = None                # 左子树
        self.right = None               # 右子树
        self.left_thread = None         # 左线索
        self.right_thread = None        # 右线索


# 插入路由表项
def insert(root, node):
    if root is None:
        return node
    if node.destination < root.destination:
        root.left = insert(root.left, node)
    elif node.destination > root.destination:
        root.right = insert(root.right, node)
    return root


# 线索化二叉查找树（通过线程链接前驱和后继）
def thread_tree(root):
    # 中序遍历并为每个节点添加线索
    prev = None

    def inorder(node):
        nonlocal prev
        if node is None:
            return
        inorder(node.left)

        # 处理左线索
        if node.left is None:
            node.left_thread = prev
        if prev is not None and prev.right is None:
            prev.right_thread = node

        prev = node
        inorder(node.right)

    inorder(root)


# 查找目标路由
def search_route(root, destination):
    if root is None:
        return None
    
    # 递归查找
    if destination < root.destination:
        return search_route(root.left, destination)
    elif destination > root.destination:
        return search_route(root.right, destination)
    else:
        return root  # 找到匹配的路由


# 打印路由信息（中文输出）
def print_route(node):
    if node:
        print(f"目标网络: {node.destination}, 子网掩码: {node.subnet_mask}, 下一跳: {node.next_hop}, 度量值: {node.metric}")


# 构建路由表树
def build_route_tree(route_list):
    root = None
    for route in route_list:
        node = RouterNode(route['destination'], route['subnet_mask'], route['next_hop'], route['metric'])
        root = insert(root, node)
    thread_tree(root)
    return root


# 测试数据
route_list = [
    {'destination': '192.168.0.0', 'subnet_mask': '255.255.255.0', 'next_hop': '192.168.0.1', 'metric': 10},
    {'destination': '10.0.0.0', 'subnet_mask': '255.0.0.0', 'next_hop': '10.0.0.1', 'metric': 5},
    {'destination': '192.168.1.0', 'subnet_mask': '255.255.255.0', 'next_hop': '192.168.1.1', 'metric': 20},
    {'destination': '172.16.0.0', 'subnet_mask': '255.240.0.0', 'next_hop': '172.16.0.1', 'metric': 15}
]

# 构建二叉查找树，并线索化
root = build_route_tree(route_list)

# 查找路由
destination_to_find = '192.168.0.0'
node = search_route(root, destination_to_find)

# 打印查找结果（中文输出）
if node:
    print(f"找到目标网络 {destination_to_find} 的路由信息：")
    print_route(node)
else:
    print(f"未找到目标网络 {destination_to_find} 的路由信息。")
