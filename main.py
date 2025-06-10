import tkinter as tk
import tkinter.ttk as ttk
from components.header import Header
from components.sidebar import Sidebar
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from components.traversal_bar import TraversalBar
from visualizer.bst_visualizer import BSTVisualizer
from visualizer.avl_visualizer import AVLVisualizer

# Map các visualizer
visualizers = {
    "Binary Tree": BinaryTreeVisualizer,
    "Binary Search Tree": BSTVisualizer,
    "AVL Tree": AVLVisualizer
}

def setup_visualizer(VisualizerClass, sidebar, right_frame):
    # Xóa các widget cũ trong right_frame (nếu có)
    for widget in right_frame.winfo_children():
        widget.destroy()

    # === Style cho ttk.Scrollbar ===
    style = ttk.Style()
    style.theme_use("clam")  # Quan trọng để chỉnh màu
    style.configure("Custom.Horizontal.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")
    style.configure("Custom.Vertical.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")

    # === Canvas Scroll Wrapper ===
    canvas_frame = tk.Frame(right_frame, bg="lightgrey")
    canvas_frame.pack(fill="both", expand=True)

    # === Scrollbars dùng ttk.Scrollbar ===
    x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal",
                             style="Custom.Horizontal.TScrollbar")
    x_scroll.pack(side="bottom", fill="x")

    y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical",
                             style="Custom.Vertical.TScrollbar")
    y_scroll.pack(side="right", fill="y")

    canvas = tk.Canvas(canvas_frame, bg="lightgrey",
                       xscrollcommand=x_scroll.set,
                       yscrollcommand=y_scroll.set)
    canvas.pack(fill="both", expand=True)

    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)    # Xóa các widget cũ trong right_frame (nếu có)
    for widget in right_frame.winfo_children():
        widget.destroy()

    # === Style cho ttk.Scrollbar ===
    style = ttk.Style()
    style.theme_use("clam")  # Quan trọng để chỉnh màu
    style.configure("Custom.Horizontal.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")
    style.configure("Custom.Vertical.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")

    # === Canvas Scroll Wrapper ===
    canvas_frame = tk.Frame(right_frame, bg="lightgrey")
    canvas_frame.pack(fill="both", expand=True)

    # === Scrollbars dùng ttk.Scrollbar ===
    x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal",
                             style="Custom.Horizontal.TScrollbar")
    x_scroll.pack(side="bottom", fill="x")

    y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical",
                             style="Custom.Vertical.TScrollbar")
    y_scroll.pack(side="right", fill="y")

    canvas = tk.Canvas(canvas_frame, bg="lightgrey",
                       xscrollcommand=x_scroll.set,
                       yscrollcommand=y_scroll.set)
    canvas.pack(fill="both", expand=True)

    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)    # Xóa các widget cũ trong right_frame (nếu có)
    for widget in right_frame.winfo_children():
        widget.destroy()

    # === Style cho ttk.Scrollbar ===
    style = ttk.Style()
    style.theme_use("clam")  # Quan trọng để chỉnh màu
    style.configure("Custom.Horizontal.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")
    style.configure("Custom.Vertical.TScrollbar",
                    troughcolor="#eeeeee",
                    background="#cccccc",
                    arrowcolor="#333333")

    # === Canvas Scroll Wrapper ===
    canvas_frame = tk.Frame(right_frame, bg="lightgrey")
    canvas_frame.pack(fill="both", expand=True)

    # === Scrollbars dùng ttk.Scrollbar ===
    x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal",
                             style="Custom.Horizontal.TScrollbar")
    x_scroll.pack(side="bottom", fill="x")

    y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical",
                             style="Custom.Vertical.TScrollbar")
    y_scroll.pack(side="right", fill="y")

    canvas = tk.Canvas(canvas_frame, bg="lightgrey",
                       xscrollcommand=x_scroll.set,
                       yscrollcommand=y_scroll.set)
    canvas.pack(fill="both", expand=True)

    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)

    # Visualizer
    visualizer = VisualizerClass(canvas)
    visualizer.bind_click_event()
    sidebar.visualizer = visualizer
    visualizer.sidebar = sidebar
    sidebar.tree_root = getattr(visualizer, "root", None)  # Đảm bảo đồng bộ

    # Traversal bar (fixed below canvas)
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)
    traversal_bar.pack(side="bottom", fill="x")
    visualizer.set_controller(traversal_bar)
    return visualizer

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.title("Tree Management")

    # Header frame trên cùng
    header_frame = tk.Frame(root, bg="white")
    header_frame.pack(side="top", fill="x")

    # Main frame chứa sidebar + right side
    main_frame = tk.Frame(root, bg="grey")
    main_frame.pack(side="top", fill="both", expand=True)

    # Sidebar
    sidebar = Sidebar(main_frame)
    sidebar.pack(side="left", fill="y")

    # Right frame
    right_frame = tk.Frame(main_frame, bg="lightgrey")
    right_frame.pack(side="left", fill="both", expand=True)

    # Header on top (sau khi đã có sidebar)
    def on_menu_click(name):
        header.set_active(name)
        VisualizerClass = visualizers[name]
        global visualizer
        visualizer = setup_visualizer(VisualizerClass, sidebar, right_frame)
        sidebar.set_visualizer(visualizer)

    header = Header(header_frame, sidebar, on_menu_click=on_menu_click)
    header.set_active("Binary Tree")

    # Khởi tạo mặc định là Binary Tree
    visualizer = setup_visualizer(BinaryTreeVisualizer, sidebar, right_frame)
    sidebar.visualizer

    root.mainloop()