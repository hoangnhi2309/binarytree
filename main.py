import tkinter as tk
import ttkbootstrap as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import random

# ==== Cây nhị phân đơn giản ====

class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None

class BinaryTreeVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_radius = 20
        self.level_height = 80
        self.highlighted_node = None
        self.nodes_positions = []
        self.root = None  # Root tree

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def bind_click_event(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        x_click, y_click = event.x, event.y
        for x, y, node in self.nodes_positions:
            dx = x_click - x
            dy = y_click - y
            distance = (dx**2 + dy**2) ** 0.5
            if distance <= self.node_radius:
                self.add_random_child(node)
                self.draw_tree(self.root)
                break

    def add_random_child(self, node):
        new_value = random.randint(1, 100)
        new_node = TreeNode(new_value)
        direction = random.choice(["left", "right"])
        if direction == "left":
            if node.left is None:
                node.left = new_node
            elif node.right is None:
                node.right = new_node
        else:
            if node.right is None:
                node.right = new_node
            elif node.left is None:
                node.left = new_node
        # Nếu cả 2 bên đều có rồi thì không thêm gì

    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []
        if root:
            self._draw_subtree(root, 500, 40, 250)

    def _draw_subtree(self, node, x, y, x_offset):
        if node.left:
            self.canvas.create_line(x, y, x - x_offset, y + self.level_height)
            self._draw_subtree(node.left, x - x_offset, y + self.level_height, x_offset // 2)
        if node.right:
            self.canvas.create_line(x, y, x + x_offset, y + self.level_height)
            self._draw_subtree(node.right, x + x_offset, y + self.level_height, x_offset // 2)

        color = "red" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", 12, "bold"))
        self.nodes_positions.append((x, y, node))


# ==== HEADER ====

class Header(tk.Frame):
    def __init__(self, parent, on_menu_click):
        super().__init__(parent, bg="#b0b0b0")
        self.pack(fill='x')

        self.on_menu_click = on_menu_click
        self.menu_buttons = {}  # Lưu các nút menu

        logo_image = Image.open("binarytree.png").resize((75, 75))
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self, image=self.logo_photo, bg="#b0b0b0")
        logo_label.pack(side="left", padx=(10, 5), pady=5)

        menu_items = ["Binary Tree", "Binary Search Tree", "AVL Tree"]
        for item in menu_items:
            normal_font = ("Arial", 20, "bold")
            underline_font = ("Arial", 20, "bold", "underline")

            btn = tk.Label(self, text=item, font=normal_font,
                           bg="#b0b0b0", fg="black", cursor="hand2")
            btn.pack(side="left", padx=30)
            normal_font = ("Arial", 20, "bold")

            underline_font = ("Arial", 20, "bold", "underline")
            underline_thin_font = ("Arial", 20, "bold", "underline", "1")
            btn.bind("<Enter>", lambda e, b=btn: b.config(font=underline_font))
            btn.bind("<Leave>", lambda e, b=btn: b.config(font=normal_font))
            btn.bind("<Button-1>", lambda e, name=item: self.menu_clicked(name))

            self.menu_buttons[item] = btn

    def menu_clicked(self, name):
        self.set_active(name)
        self.on_menu_click(name)

    def set_active(self, active_name):
        for name, btn in self.menu_buttons.items():
            if name == active_name:
                btn.config(fg="#164933", font=("Arial", 20, "bold", "underline"))
            else:
                btn.config(fg="black", font=("Arial", 20, "bold"))

# ==== SIDEBAR ====
class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="grey", width=400)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)
        self.tree_root = None
        self.array = []
        self.visualizer = None
        self.highlighted_node = None

        array_label = tk.Label(self, text="Array:", font=("Arial", 20, "bold"), bg="grey", fg="black")
        array_label.pack(anchor="w", padx=20, pady=(0, 1))

        self.array_display = tk.Label(
            self,
            text="",
            bg="white",
            font=("Arial", 16),
            anchor="n",
            justify="left",
            height=20,
            bd=10,
            relief="flat"
        )
        self.array_display.pack(padx=20, fill="x", pady=(0, 20))

        search_title = tk.Label(self, text="Find:", font=("Arial", 18, "bold"), bg="grey", fg="black")
        search_title.pack(anchor="w", padx=20, pady=(10, 5))

        search_frame = tk.Frame(self, relief="flat", bg="grey", bd=5, highlightthickness=0)
        search_frame.pack(fill="x", padx=20)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(side="left", fill="x", expand=True)

        search_btn = tk.Button(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            relief="flat",
            bg="grey",
            command=self.on_search_node
        )
        search_btn.pack(side="left", padx=(5, 0))

        self.create_modern_button("Create random tree", self.on_random_tree)
        self.create_modern_button("Delete", self.on_clear_tree)

    def on_search_node(self):
        value = self.search_entry.get()
        if value.isdigit():
            value = int(value)
            if value in self.array:
                self.highlighted_node = self._find_node(self.tree_root, value)
                if self.visualizer:
                    self.visualizer.highlighted_node = self.highlighted_node
                    self.visualizer.draw_tree(self.tree_root)
            else:
                messagebox.showinfo("Node Not Found", f"Node {value} not found in the array.")
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

    def _find_node(self, root, value):
        if root is None:
            return None
        if root.val == value:
            return root
        left_result = self._find_node(root.left, value)
        if left_result:
            return left_result
        return self._find_node(root.right, value)

    def on_random_tree(self):
        self.array = random.sample(range(1, 100), 7)
        self.array_display.config(text=str(self.array))
        self.tree_root = self.build_tree_from_list(self.array)
        if self.visualizer:
            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)

    def on_clear_tree(self):
        self.tree_root = None
        self.array = []
        self.highlighted_node = None
        self.array_display.config(text="")
        if self.visualizer:
            self.visualizer.canvas.delete("all")

    def build_tree_from_list(self, lst):
        if not lst:
            return None
        nodes = [TreeNode(val) for val in lst]
        for i in range(len(lst)):
            left_index = 2 * i + 1
            right_index = 2 * i + 2
            if left_index < len(lst):
                nodes[i].left = nodes[left_index]
            if right_index < len(lst):
                nodes[i].right = nodes[right_index]
        return nodes[0]

    def create_modern_button(self, text, command):
        btn = tk.Label(
            self,
            text=text,
            font=("Arial", 14),
            bg="#ffffff",
            fg="#333333",
            bd=2,
            cursor="hand2"
        )
        btn.pack(padx=20, fill="x", pady=(10, 5))
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="white"))
        btn.bind("<Button-1>", lambda e: command())


# ==== MAIN ====
if __name__ == "__main__":
    def show_page(name):
        print(f"Chuyển đến trang: {name}")
        header.set_active(name)  # Cập nhật màu menu
        
        # Tùy theo tên trang, bạn có thể thay đổi nội dung main_area
        # Ví dụ: xóa canvas cũ, tạo cây mới, v.v.

    root = tk.Tk()
    root.geometry("1200x700")
    root.title("TreeSim")

    # Truyền show_page cho Header
    header = Header(root, on_menu_click=show_page)
    
    sidebar = Sidebar(root)

    main_area = tk.Canvas(root, bg="lightgrey")
    main_area.pack(side="left", fill="both", expand=True)

    visualizer = BinaryTreeVisualizer(main_area)
    visualizer.bind_click_event()

    sidebar.visualizer = visualizer

    # Chọn trang mặc định là "Binary Tree"
    header.set_active("Binary Tree")

    root.mainloop()

