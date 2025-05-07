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

    # Header on top
    header = Header(root, on_menu_click=lambda name: print(f"Chuyển đến {name}"))
    header.set_active("Binary Tree")  

    # Main frame containing Sidebar and visualization area
    main_frame = tk.Frame(root, bg="grey")
    main_frame.pack(fill="both", expand=True)

    # Sidebar on the left
    sidebar = Sidebar(main_frame)
    sidebar.pack(side="left", fill="y")
    
    # Right frame: contains canvas + traversal bar
    right_frame = tk.Frame(main_frame, bg="lightgrey")
    right_frame.pack(side="left", fill="both", expand=True)

    # Canvas for drawing the tree
    main_area = tk.Canvas(right_frame, bg="lightgrey")
    main_area.pack(fill="both", expand=True)  # Fixed expandx to expand=True

    # Visualizer attached to the canvas
    visualizer = BinaryTreeVisualizer(main_area)
    visualizer.bind_click_event()  # Make sure this method is correctly defined in BinaryTreeVisualizer

    # Assign visualizer and controller to the sidebar
    sidebar.visualizer = visualizer
    sidebar.controller = visualizer.controller  # Ensure the controller is correctly assigned

    # Ensure sidebar has a tree_root initialized and passed to traversal bar
    sidebar.tree_root = None  # or initialize it with an empty tree or root node as needed

    # Traversal bar attached at the bottom of the canvas area
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)

    root.mainloop()
