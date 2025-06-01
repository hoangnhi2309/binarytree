import tkinter as tk
import tkinter.messagebox
import random
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer, TreeNode
from visualizer.avl_visualizer import AVLVisualizer
from components.sidebar import Sidebar
from components.header import Header
from components.traversal_bar import TraversalBar


# --- BST Visualizer kế thừa BinaryTreeVisualizer ---
class BSTVisualizer(BinaryTreeVisualizer):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.selected_node = None  # node đang được chọn
        
    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None

        if num_nodes == 1:
            values = [min_val]
        elif num_nodes == 2:
            values = [min_val, max_val]
        else:
            middle_nodes = random.sample(range(min_val + 1, max_val), num_nodes - 2)
            values = [min_val] + middle_nodes + [max_val]
            random.shuffle(values)

        def insert_bst(root, val):
            if not root:
                return TreeNode(val)
            if val < root.val:
                root.left = insert_bst(root.left, val)
            elif val > root.val:
                root.right = insert_bst(root.right, val)
            return root

        root = None
        for val in values:
            root = insert_bst(root, val)
        return root
    def on_random_tree(self):
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.on_random_tree()
        else:
            tk.messagebox.showerror("Error", "Sidebar not found!")


# --- Map các visualizer ---
visualizers = {
    "Binary Tree": BinaryTreeVisualizer,
    "BST": BSTVisualizer,
    "AVL Tree": AVLVisualizer,
}


# --- Cài đặt visualizer tương ứng ---
def setup_visualizer(VisualizerClass, sidebar, right_frame):
    for widget in right_frame.winfo_children():
        widget.destroy()

    canvas_frame = tk.Frame(right_frame, bg="lightgrey")
    canvas_frame.pack(fill="both", expand=True)

    x_scroll = tk.Scrollbar(canvas_frame, orient="horizontal")
    x_scroll.pack(side="bottom", fill="x")
    y_scroll = tk.Scrollbar(canvas_frame, orient="vertical")
    y_scroll.pack(side="right", fill="y")

    canvas = tk.Canvas(canvas_frame, bg="lightgrey",
                       xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    canvas.pack(fill="both", expand=True)

    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)

    visualizer = VisualizerClass(canvas)
    visualizer.bind_click_event()

    sidebar.visualizer = visualizer
    if hasattr(visualizer, "controller"):
        sidebar.controller = visualizer.controller
    visualizer.sidebar = sidebar

    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)
    traversal_bar.pack(side="bottom", fill="x")
    visualizer.set_controller(traversal_bar)

    return visualizer


# --- Sidebar mở popup tạo cây ---

def on_random_tree(self):
    self.popup = tk.Toplevel(self)
    self.popup.title("Create Random Tree")
    self.popup.geometry("300x250")
    self.popup.transient(self.winfo_toplevel())

    tk.Label(self.popup, text="Min Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(10, 2))
    self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
    self.min_entry.insert(0, "1")
    self.min_entry.pack(fill="x", padx=10, pady=(0, 10))

    tk.Label(self.popup, text="Max Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
    self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
    self.max_entry.insert(0, "99")
    self.max_entry.pack(fill="x", padx=10, pady=(0, 10))

    from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
    from visualizer.bst_visualizer import BSTVisualizer

    if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, BSTVisualizer):
        label_text = "Tree Depth:"
    else:
        label_text = "Number of Nodes:"

    tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
    self.extra_entry = tk.Entry(self.popup, font=("Arial", 12))
    self.extra_entry.insert(0, "10")
    self.extra_entry.pack(fill="x", padx=10, pady=(0, 10))

    cancel_button = tk.Button(self.popup, text="Cancel", command=self.popup.destroy,
                              font=("Arial", 12), bg="grey", fg="black")
    cancel_button.pack(side="right", padx=(0, 5), pady=10)

    create_button = tk.Button(self.popup, text="Create", command=self.handle_create_tree,
                              font=("Arial", 12), bg="grey", fg="white")
    


# --- Hàm tạo cây khi nhấn "Create" ---
def handle_create_tree(self):
    try:
        min_val = int(self.min_entry.get())
        max_val = int(self.max_entry.get())
        extra = int(self.extra_entry.get())

        if min_val > max_val or extra <= 0:
            raise ValueError("Min > Max hoặc extra <= 0")

        self.tree_root = self.visualizer.create_random_tree(min_val, max_val, extra)

        if self.tree_root is None:
            raise ValueError("Không tạo được cây")

        self.visualizer.set_root(self.tree_root)
        self.visualizer.draw_tree(self.tree_root)

        if hasattr(self, "tree_to_array") and hasattr(self, "update_array_display"):
            self.array = self.tree_to_array(self.tree_root)
            self.update_array_display(self.array)

        self.popup.destroy()

    except Exception as e:
        print("DEBUG ERROR:", e)
        tk.messagebox.showerror("Lỗi", "Thông số không hợp lệ hoặc không tạo được cây.")

def show_canvas_menu(self, event):
    menu = tk.Menu(self.canvas, tearoff=0)
    menu.add_command(label="Find node", command=self.on_find_node)
    menu.add_command(label="Create random tree", command=self.on_random_tree)
    # ...
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


# --- Sidebar class chính ---
class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgrey", width=300)

        self.visualizer = None
        self.tree_root = None
        self.popup = None  # để tránh lỗi chưa khai báo

        self.create_random_tree_btn = tk.Button(
            self, text="Create random tree", command=lambda: self.visualizer.on_random_tree(),
            font=("Arial", 12), bg="grey", fg="white"
        )
        self.create_random_tree_btn.pack(pady=10, padx=10, fill="x")

    def on_random_tree(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.winfo_toplevel())

        tk.Label(self.popup, text="Min Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.min_entry.insert(0, "1")
        self.min_entry.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(self.popup, text="Max Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.max_entry.insert(0, "99")
        self.max_entry.pack(fill="x", padx=10, pady=(0, 10))

        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, BSTVisualizer):
            label_text = "Tree Depth:"
        else:
            label_text = "Number of Nodes:"

        tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.extra_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.extra_entry.insert(0, "3")
        self.extra_entry.pack(fill="x", padx=10, pady=(0, 10))

        cancel_button = tk.Button(self.popup, text="Cancel", command=self.popup.destroy,
                                  font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5), pady=10)

        create_button = tk.Button(self.popup, text="Create", command=self.handle_create_tree,
                                  font=("Arial", 12), bg="grey", fg="white")
        create_button.pack(side="right", padx=(5, 0), pady=10)

    def handle_create_tree(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            extra = int(self.extra_entry.get())

            if min_val > max_val or extra <= 0:
                raise ValueError("Min > Max hoặc extra <= 0")

            self.tree_root = self.visualizer.create_random_tree(min_val, max_val, extra)

            if self.tree_root is None:
                raise ValueError("Không tạo được cây")

            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)

            if hasattr(self, "tree_to_array") and hasattr(self, "update_array_display"):
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)

            self.popup.destroy()

        except Exception as e:
            print("DEBUG ERROR:", e)
            tk.messagebox.showerror("Lỗi", "Thông số không hợp lệ hoặc không tạo được cây.")

    def on_array_value_change(self, new_value, index):
        if self.visualizer.selected_node:
            self.visualizer.selected_node.val = new_value
            self.visualizer.draw_tree(self.tree_root)
        else:
            tk.messagebox.showinfo("Info", "Hãy chọn một node trên cây trước khi sửa giá trị.")

    def update_array_display(self, array):
        # Lưu lại array hiện tại để dùng cho update
        self.array = array.copy()
        # Xóa frame cũ nếu có
        if hasattr(self, "array_frame"):
            self.array_frame.destroy()
        self.array_frame = tk.Frame(self)
        self.array_frame.pack(pady=10)

        self.array_entries = []
        for i, val in enumerate(array):
            entry = tk.Entry(self.array_frame, width=5, font=("Arial", 12))
            entry.insert(0, str(val))
            entry.grid(row=0, column=i, padx=2)
            self.array_entries.append(entry)

        # Thêm nút Update Tree
        update_btn = tk.Button(self.array_frame, text="Update Tree", font=("Arial", 12), bg="blue", fg="white",
                               command=self.on_update_tree)
        update_btn.grid(row=1, column=0, columnspan=len(array), pady=5)
            
    def on_update_tree(self):
        try:
            new_values = [int(entry.get()) for entry in self.array_entries]
            if self.visualizer.selected_node is not None:
                # Tìm vị trí của node đang chọn trong thứ tự inorder
                inorder_nodes = []
                def inorder(node):
                    if not node:
                        return
                    inorder(node.left)
                    inorder_nodes.append(node)
                    inorder(node.right)
                inorder(self.tree_root)
                # Xác định vị trí node đang chọn
                try:
                    selected_idx = inorder_nodes.index(self.visualizer.selected_node)
                except ValueError:
                    tk.messagebox.showerror("Lỗi", "Không tìm thấy node được chọn.")
                    return
                # Cập nhật giá trị node đang chọn
                self.visualizer.selected_node.val = new_values[selected_idx]
                self.visualizer.draw_tree(self.tree_root)
                # Cập nhật lại array để đồng bộ
                if hasattr(self, "tree_to_array"):
                    self.array = self.tree_to_array(self.tree_root)
                    self.update_array_display(self.array)
            else:
                tk.messagebox.showinfo("Info", "Hãy chọn một node trên cây trước khi update.")
        except Exception as e:
            tk.messagebox.showerror("Lỗi", "Giá trị nhập không hợp lệ.")

    def tree_to_array(self, root):
        res = []
        def inorder(node):
            if not node:
                return
            inorder(node.left)
            res.append(node.val)
            inorder(node.right)
        inorder(root)
        return res