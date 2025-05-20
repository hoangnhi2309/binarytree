import tkinter as tk
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

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("Tree Management")

    # 1. Tạo header trước để nó nằm trên cùng
    header = Header(root, None, None)
    header.pack(side="top", fill="x")

    # 2. Main content dưới header
    main_frame = tk.Frame(root, bg="grey")
    main_frame.pack(fill="both", expand=True)

    # 3. Sidebar bên trái
    sidebar = Sidebar(main_frame)
    sidebar.pack(side="left", fill="y")

    # 4. Right side (canvas + traversal)
    right_frame = tk.Frame(main_frame, bg="lightgrey")
    right_frame.pack(side="left", fill="both", expand=True)

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

    # 5. Biến toàn cục
    current_visualizer = None
    traversal_bar = None

    # 6. Hàm xử lý khi click menu
    def on_menu_click(name):
        global current_visualizer, traversal_bar

        header.set_active(name)
 # Xóa visualizer cũ nếu có
        if current_visualizer:
            current_visualizer.clear_canvas()   # Xóa canvas cũ
            current_visualizer.destroy()
            current_visualizer = None

        if traversal_bar:
            traversal_bar.destroy()
            traversal_bar = None

        # Xóa dữ liệu cây trong sidebar
        sidebar.tree_root = None
        sidebar.array = []
        sidebar.update_array_display()  # Hoặc clear widget hiển thị mảng

        VisualizerClass = visualizers.get(name, BinaryTreeVisualizer)
        current_visualizer = VisualizerClass(canvas)
        current_visualizer.bind_click_event()

        sidebar.visualizer = current_visualizer
        sidebar.controller = current_visualizer.controller
        current_visualizer.sidebar = sidebar

        traversal_bar = TraversalBar(right_frame, current_visualizer, tree_getter=lambda: sidebar.tree_root)
        traversal_bar.pack(side="bottom", fill="x")
        current_visualizer.set_controller(traversal_bar)

    # 7. Gán lại sidebar + callback cho header
    header.sidebar = sidebar
    header.on_menu_click = on_menu_click
    header.set_active("Binary Tree")

    # 8. Visualizer mặc định
    current_visualizer = BinaryTreeVisualizer(canvas)
    current_visualizer.bind_click_event()
    sidebar.visualizer = current_visualizer
    sidebar.controller = current_visualizer.controller
    current_visualizer.sidebar = sidebar

    traversal_bar = TraversalBar(right_frame, current_visualizer, tree_getter=lambda: sidebar.tree_root)
    traversal_bar.pack(side="bottom", fill="x")
    current_visualizer.set_controller(traversal_bar)

    root.mainloop()
