import tkinter as tk
from tkinter import messagebox
import random

# ------------------- Cấu trúc dữ liệu -------------------

class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None
        self.height = 1  # Cần cho AVL

class AVLTree:
    def insert(self, root, key):
        if not root:
            return TreeNode(key)
        elif key < root.val:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)

        # Cập nhật chiều cao
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Kiểm tra hệ số cân bằng
        balance = self.get_balance(root)

        # Các trường hợp xoay
        if balance > 1 and key < root.left.val:
            return self.right_rotate(root)
        if balance < -1 and key > root.right.val:
            return self.left_rotate(root)
        if balance > 1 and key > root.left.val:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.val:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def left_rotate(self, z):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def right_rotate(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

# ------------------- Giao diện hiển thị -------------------

class AVLVisualizer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.label = tk.Label(self, text="AVL Tree View", font=("Arial", 24), bg="white")
        self.label.pack(pady=20)

        # Canvas để vẽ cây
        self.canvas = tk.Canvas(self, bg="white", height=400)
        self.canvas.pack(fill="both", expand=True)

        # Cây AVL
        self.tree = AVLTree()
        self.root = None

        # Ô nhập và nút thêm node
        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        self.button = tk.Button(self, text="Thêm Node", command=self.insert_node)
        self.button.pack()

    def insert_node(self):
        try:
            value = int(self.entry.get())
            self.root = self.tree.insert(self.root, value)
            self.entry.delete(0, tk.END)
            self.draw_tree(self.root)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên.")

    def draw_tree(self, node, x=400, y=50, dx=100):
        self.canvas.delete("all")
        self._draw_tree_recursive(node, x, y, dx)

    def _draw_tree_recursive(self, node, x, y, dx):
        if node is None:
            return
        radius = 20
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightblue")
        self.canvas.create_text(x, y, text=str(node.val))

        if node.left:
            self.canvas.create_line(x, y + radius, x - dx, y + 60 - radius)
            self._draw_tree_recursive(node.left, x - dx, y + 60, dx // 2)
        if node.right:
            self.canvas.create_line(x, y + radius, x + dx, y + 60 - radius)
            self._draw_tree_recursive(node.right, x + dx, y + 60, dx // 2)

    def bind_click_event(self):
        pass  # Chưa cần dùng

    def set_controller(self, controller):
        pass  # Chưa cần dùng
