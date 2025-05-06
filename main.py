from tkinter import Tk, Frame
import tkinter as tk
from components.header import Header
from components.sidebar import Sidebar
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from components.traversal_bar import TraversalBar
from controller import Controller
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("TreeSim")

    # Header trên cùng
    header = Header(root, on_menu_click=lambda name: print(f"Chuyển đến {name}"))
    header.set_active("Binary Tree")  

    # Khung lớn chứa Sidebar và vùng hiển thị
    main_frame = tk.Frame(root, bg="grey")
    main_frame.pack(fill="both", expand=True)

    # Sidebar bên trái
    sidebar = Sidebar(main_frame)
    sidebar.pack(side="left", fill="y")
    
    # Khung phải: chứa canvas + traversal bar
    right_frame = tk.Frame(main_frame, bg="lightgrey")
    right_frame.pack(side="left", fill="both", expand=True)

    # Vùng vẽ cây
    main_area = tk.Canvas(right_frame, bg="lightgrey")
    main_area.pack(fill="both", expand=True)

    # Visualizer gắn vào canvas
    visualizer = BinaryTreeVisualizer(main_area)
    visualizer.bind_click_event()
    sidebar.visualizer = visualizer
    sidebar.controller = visualizer.controller  # Gán controller cho sidebar
    # Traversal bar gắn vào dưới cùng của vùng vẽ
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)

    root.mainloop()