# === main.py === tk
import tkinter as tk
import random
from components.header import Header
from components.sidebar import Sidebar
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from components.traversal_bar import TraversalBar
from visualizer.avl_visualizer import AVLVisualizer
from controller import Controller

# Import TreeNode class
from visualizer.binary_tree_visualizer import TreeNode

# Map các visualizer
visualizers = {
    "Binary Tree": BinaryTreeVisualizer,
    "AVL Tree": AVLVisualizer
}

from visualizer.binary_tree_visualizer import BinaryTreeVisualizer

class BSTVisualizer(BinaryTreeVisualizer):
    # Nếu muốn thêm/chỉnh sửa gì riêng cho BST thì override ở đây
    pass

    # Hàm tạo BST ngẫu nhiên đúng chuẩn BST
    def create_random_tree(self, min_val, max_val, depth):
        if depth <= 0 or min_val > max_val:
            return None
        val = random.randint(min_val, max_val)
        node = TreeNode(val)
        if depth > 1:
            # Cây con trái: giá trị nhỏ hơn node hiện tại
            node.left = self.create_random_tree(min_val, val - 1, depth - 1)
            # Cây con phải: giá trị lớn hơn hoặc bằng node hiện tại
            node.right = self.create_random_tree(val, max_val, depth - 1)
        return node

def setup_visualizer(VisualizerClass, sidebar, right_frame):
    # Xóa các widget cũ trong right_frame (nếu có)
    for widget in right_frame.winfo_children():
        widget.destroy()

    # === Canvas Scroll Wrapper ===
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

    # Khi tạo menu chuột phải trên canvas
    menu = tk.Menu(canvas, tearoff=0)
    menu.add_command(label="Create tree", command=visualizer.on_random_tree)

    # Visualizer
    visualizer = VisualizerClass(canvas)
    visualizer.bind_click_event()
    sidebar.visualizer = visualizer
    if hasattr(visualizer, "controller"):
        sidebar.controller = visualizer.controller
    visualizer.sidebar = sidebar

    # Traversal bar (fixed below canvas)
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)
    traversal_bar.pack(side="bottom", fill="x")
    visualizer.set_controller(traversal_bar)
    return visualizer

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("Tree Management")

    # Header on top
    def on_menu_click(name):
        header.set_active(name)
        VisualizerClass = visualizers[name]
        global visualizer
        visualizer = setup_visualizer(VisualizerClass, sidebar, right_frame)

    header = Header(root, on_menu_click=on_menu_click)
    header.set_active("Binary Tree")

    # Main frame contains sidebar + right side
    main_frame = tk.Frame(root, bg="grey")
    main_frame.pack(fill="both", expand=True)

    # Sidebar
    sidebar = Sidebar(main_frame)
    sidebar.pack(side="left", fill="y")

    # Right frame
    right_frame = tk.Frame(main_frame, bg="lightgrey")
    right_frame.pack(side="left", fill="both", expand=True)

    # Khởi tạo mặc định là Binary Tree
    visualizer = setup_visualizer(BinaryTreeVisualizer, sidebar, right_frame)

    # Example popup with button
    def create_tree_and_close():
        # Logic to create tree
        popup.destroy()

    popup = tk.Toplevel(root)
    

    root.mainloop()

