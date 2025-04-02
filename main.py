import tkinter as tk
from tkinter import messagebox

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)

    def inorder(self, node):
        if node:
            self.inorder(node.left)
            print(node.value, end=" ")
            self.inorder(node.right)

class BinaryTreeApp:
    def __init__(self, root):
        self.tree = BinaryTree()
        self.window = root
        self.window.title("Quản lý Cây Nhị Phân")

        # Cửa sổ giao diện
        self.canvas = tk.Canvas(self.window, width=600, height=400, bg="white")
        self.canvas.pack()

        # Các widget
        self.label = tk.Label(self.window, text="Nhập giá trị:")
        self.label.pack()

        self.entry = tk.Entry(self.window)
        self.entry.pack()

        self.insert_button = tk.Button(self.window, text="Thêm vào cây", command=self.insert_value)
        self.insert_button.pack()

        self.display_button = tk.Button(self.window, text="Hiển thị cây", command=self.display_tree)
        self.display_button.pack()

    def insert_value(self):
        value = self.entry.get()
        if value.isdigit():
            self.tree.insert(int(value))
            messagebox.showinfo("Thông báo", f"Đã thêm {value} vào cây.")
            self.entry.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị hợp lệ.")

    def display_tree(self):
        self.canvas.delete("all")
        self._draw_tree(self.tree.root, 300, 50, 100, 50)

    def _draw_tree(self, node, x, y, dx, dy):
        if node:
            # Vẽ nút
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue")
            self.canvas.create_text(x, y, text=str(node.value))

            # Vẽ nhánh trái
            if node.left:
                self.canvas.create_line(x, y+20, x-dx, y+dy-20, arrow=tk.LAST)
                self._draw_tree(node.left, x-dx, y+dy, dx//2, dy)

            # Vẽ nhánh phải
            if node.right:
                self.canvas.create_line(x, y+20, x+dx, y+dy-20, arrow=tk.LAST)
                self._draw_tree(node.right, x+dx, y+dy, dx//2, dy)

# Khởi tạo giao diện
root = tk.Tk()
app = BinaryTreeApp(root)
root.mainloop()

