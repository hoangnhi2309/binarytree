import tkinter as tk
import random

# ==== Tạo giao diện ====
root = tk.Tk()
root.title("Binary Tree")
root.geometry("1000x600")
root.configure(bg="#e5e5e5")

# ====== Menu ngang ======
menu_frame = tk.Frame(root, bg="#384F41", height=50)
menu_frame.pack(fill="x")
menu_items = ["Binary Tree", "Binary Search Tree", "AVL Tree"]
labels = []

# ====== Hover ======
def on_enter(event):
    event.widget.config(fg="white")
def on_leave(event):
    event.widget.config(fg="#facc45")

for i, item in enumerate(menu_items):
    container = tk.Frame(menu_frame, bg="#1b501b")
    container.grid(row=0, column=i, sticky="nsew")
    menu_frame.grid_columnconfigure(i, weight=1)

    btn = tk.Label(
        menu_frame, text=item,
        font=("Arial", 16, "bold"),
        fg="#facc45", bg="#1b501b",
        width=25, height=2,
        relief="solid", bd=1
    )
    btn.grid(row=0, column=i, sticky="nsew")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    labels.append(btn)

for i in range(3):
    menu_frame.grid_columnconfigure(i, weight=1)

# ====== thanh bar_frame chứa các nút ======
wrapper = tk.Frame(root, height=40)
wrapper.pack(fill="x")

bar_frame = tk.Frame(wrapper, bg="#DCD7CD")
bar_frame.pack(fill="both", expand=True)
# Entry nhỏ để nhập giá trị node
entry = tk.Entry(bar_frame, width=10, font=("Arial", 20))
entry.pack(side="left", padx=(5, 10), pady=5)

# Các nút chức năng với style nhẹ
button_style = {
    "bg": "#d3d3d3",  # xám nhạt
    "font": ("Arial", 16, "bold"),
    "relief": "flat",
    "padx": 10,
    "pady": 5
}

btn_insert = tk.Button(bar_frame, text="Insert", command=lambda: insert_node(), **button_style)
btn_insert.pack(side="left", padx=5)

btn_delete = tk.Button(bar_frame, text="Delete", command=lambda: delete_node(), **button_style)
btn_delete.pack(side="left", padx=5)

btn_generate = tk.Button(bar_frame, text="Generate random trees", command=lambda: generate_random_tree(), **button_style)
btn_generate.pack(side="left", padx=5)

# Vùng chính để vẽ cây
main_area = tk.Frame(root, bg="#eaeaea", width=600, height=350)
main_area.pack(padx=20, pady=20, fill="both", expand=True)

# Thêm canvas để vẽ cây vào main_area
canvas = tk.Canvas(main_area, bg="#ffffff")
canvas.pack(fill="both", expand=True)

# ====== Cây nhị phân ======
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        def _insert(node, val):
            if node is None:
                return TreeNode(val)
            if val < node.value:
                node.left = _insert(node.left, val)
            else:
                node.right = _insert(node.right, val)
            return node
        self.root = _insert(self.root, value)

    def clear(self):
        self.root = None

    def generate_random(self, count=7):
        self.clear()
        for _ in range(count):
            self.insert(random.randint(1, 99))

tree = BinaryTree()

# ====== Vẽ cây lên canvas ======
def draw_tree(node, x, y, dx=80, dy=60):
    if node is None:
        return
    r = 20
    canvas.create_oval(x - r, y - r, x + r, y + r, fill="#facc45", outline="#1b501b", width=2)
    canvas.create_text(x, y, text=str(node.value), font=("Arial", 12, "bold"))

    if node.left:
        canvas.create_line(x, y + r, x - dx, y + dy - r, width=2)
        draw_tree(node.left, x - dx, y + dy, dx * 0.8, dy)
    if node.right:
        canvas.create_line(x, y + r, x + dx, y + dy - r, width=2)
        draw_tree(node.right, x + dx, y + dy, dx * 0.8, dy)

def render():
    canvas.delete("all")
    if tree.root:
        draw_tree(tree.root, 500, 40)  # vị trí bắt đầu từ giữa

# ====== Chức năng các nút ======
def insert_node():
    try:
        value = int(entry.get())
        tree.insert(value)
        render()
    except ValueError:
        print("Vui lòng nhập số nguyên hợp lệ")

def delete_node():
    tree.clear()
    render()

def generate_random_tree():
    tree.generate_random()
    render()

# ====== Chạy giao diện ======
root.mainloop()
