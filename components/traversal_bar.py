import tkinter as tk
from tkinter import ttk
import threading
import time

class TraversalBar(tk.Frame):
    def __init__(self, parent, visualizer, tree_getter):
        super().__init__(parent, bg="grey")
        self.visualizer = visualizer
        self.tree_getter = tree_getter
        self.pack(side="bottom", fill="x", padx=2, pady=(0, 2))

        self.traversal_nodes = []
        self.traversal_index = 0
        self.traversing = False
        self.paused = False
        self.traversal_thread = None

        self.grid_columnconfigure(5, weight=1)

        self.start_btn = self.create_button("Start", self.start_traversal, 0)
        self.pause_btn = self.create_button("Pause", self.toggle_pause_resume, 1)
        self.next_btn = self.create_button("Next", self.next_step, 2)
        self.stop_btn = self.create_button("Stop", self.stop_traversal, 3)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=4, padx=10, sticky="we", columnspan=2)

        self.node_label = tk.Label(self, text="Node: -", font=("Arial", 12), bg="grey", fg="black")
        self.node_label.grid(row=0, column=6, padx=(10, 2))

        tk.Label(self, text="Speed:", font=("Arial", 12), bg="grey", fg="black").grid(row=0, column=7, padx=(10, 2))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(self, from_=0.1, to=2.0, resolution=0.1,
                                    orient="horizontal", variable=self.speed_var, length=100)
        self.speed_scale.grid(row=0, column=8, padx=(0, 10))

    def create_button(self, text, command, col):
        btn = tk.Label(self, text=text, font=("Arial", 12), bg="white", fg="black",
                       padx=10, pady=3, cursor="hand2", relief="flat", bd=0)
        btn.grid(row=0, column=col, padx=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="white"))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def start_traversal(self):
        root = self.tree_getter()
        if not root:
            return
        self.traversal_nodes = self.get_bfs_list(root)
        self.traversal_index = 0
        self.traversing = True
        self.paused = False
        self.pause_btn.config(text="Pause")
        if not self.traversal_thread or not self.traversal_thread.is_alive():
            self.traversal_thread = threading.Thread(target=self.run_traversal)
            self.traversal_thread.start()

    def toggle_pause_resume(self):
        if self.traversing:
            self.paused = not self.paused
            self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def stop_traversal(self):
        self.traversing = False
        self.paused = False
        self.visualizer.highlighted_node = None
        self.visualizer.draw_tree(self.tree_getter())
        self.node_label.config(text="Node: -")
        self.progress_var.set(0)
        self.pause_btn.config(text="Pause")

    def next_step(self):
        if not self.traversal_nodes or self.traversal_index >= len(self.traversal_nodes):
            return
        node = self.traversal_nodes[self.traversal_index]
        self.visualizer.highlighted_node = node
        self.visualizer.draw_tree(self.tree_getter())
        self.node_label.config(text=f"Node: {node.val}")
        self.traversal_index += 1
        self.progress_var.set((self.traversal_index / len(self.traversal_nodes)) * 100)

    def run_traversal(self):
        while self.traversing and self.traversal_index < len(self.traversal_nodes):
            if not self.paused:
                node = self.traversal_nodes[self.traversal_index]
                self.visualizer.highlighted_node = node
                self.visualizer.draw_tree(self.tree_getter())
                self.node_label.config(text=f"Node: {node.val}")
                self.traversal_index += 1
                self.progress_var.set((self.traversal_index / len(self.traversal_nodes)) * 100)
                time.sleep(1.0 / self.speed_var.get())
            else:
                time.sleep(0.1)

    def get_bfs_list(self, root):
        result = []
        queue = [root]
        while queue:
            current = queue.pop(0)
            if current:
                result.append(current)
                queue.append(current.left)
                queue.append(current.right)
        return result