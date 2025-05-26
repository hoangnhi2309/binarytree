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

    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None

        values = random.sample(range(min_val, max_val + 1), num_nodes)
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
