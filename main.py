# === main.py ===
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

    # Header on top
    header = Header(root, on_menu_click=lambda name: print(f"Chuyển đến {name}"))
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

    # Visualizer
    visualizer = BinaryTreeVisualizer(canvas)
    visualizer.bind_click_event()
    sidebar.visualizer = visualizer
    sidebar.controller = visualizer.controller
    visualizer.sidebar = sidebar

    # Traversal bar (fixed below canvas)
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)
    visualizer.set_controller(traversal_bar)

    root.mainloop()
