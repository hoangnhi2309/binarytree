import tkinter as tk
import tkinter.messagebox
import random
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer, TreeNode


class AVLVisualizer(BinaryTreeVisualizer):
    def height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def update_height(self, node):
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def right_rotate(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self.update_height(y)
        self.update_height(x)
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self.update_height(x)
        self.update_height(y)
        return y

    def insert_avl(self, root, key):
        if not root:
            node = TreeNode(key)
            node.height = 1
            return node
        if key < root.val:
            root.left = self.insert_avl(root.left, key)
        elif key > root.val:
            root.right = self.insert_avl(root.right, key)
        else:
            return root  # bỏ qua trùng

        self.update_height(root)
        balance = self.get_balance(root)

        # Xử lý 4 case mất cân bằng
        if balance > 1 and key < root.left.val:      # Left Left
            return self.right_rotate(root)
        if balance < -1 and key > root.right.val:    # Right Right
            return self.left_rotate(root)
        if balance > 1 and key > root.left.val:      # Left Right
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.val:    # Right Left
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def delete_avl(self, root, key):
        if not root:
            return root
        if key < root.val:
            root.left = self.delete_avl(root.left, key)
        elif key > root.val:
            root.right = self.delete_avl(root.right, key)
        else:
            # Node có 1 hoặc 0 con
            if not root.left:
                temp = root.right
                root = None
                return temp
            elif not root.right:
                temp = root.left
                root = None
                return temp
            # Node có 2 con: lấy node nhỏ nhất bên phải
            temp = root.right
            while temp.left:
                temp = temp.left
            root.val = temp.val
            root.right = self.delete_avl(root.right, temp.val)

        if not root:
            return root

        self.update_height(root)
        balance = self.get_balance(root)

        # Cân bằng lại
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def get_min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None

        # Luôn lấy min và max, các giá trị còn lại lấy random
        if num_nodes == 1:
            values = [min_val]
        elif num_nodes == 2:
            values = [min_val, max_val]
        else:
            middle = list(range(min_val + 1, max_val))
            middle_nodes = random.sample(middle, num_nodes - 2)
            values = [min_val] + middle_nodes + [max_val]
            random.shuffle(values)

        root = None
        for val in values:
            root = self.insert_avl(root, val)
        return root

    def on_random_tree(self):
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.on_random_tree()
        else:
            tk.messagebox.showerror("Error", "Sidebar not found!")
    def get_array_representation(self):
        from collections import deque
        if not self.root:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

    def print_avl(self, node):
        if not node:
            return
        print(f"Node {node.val}: height={getattr(node, 'height', None)}, balance={self.get_balance(node)}")
        self.print_avl(node.left)
        self.print_avl(node.right)

# Đảm bảo TreeNode luôn có height
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1


