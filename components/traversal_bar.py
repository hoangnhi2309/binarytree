import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class TraversalBar(tk.Frame):
    def __init__(self, parent, visualizer, tree_getter):
        super().__init__(parent, bg="grey")
        self.visualizer = visualizer
        self.tree_getter = tree_getter
        self.parent = parent
        self.pack(side="bottom", fill="x", padx=2, pady=(0, 2))

        self.traversal_nodes = []
        self.traversal_index = 0
        self.traversing = False
        self.paused = False
        self.traversal_thread = None
        self.traversal_mode = "bfs"
        self.popup = None

        self.grid_columnconfigure(5, weight=1)

        self.start_btn = self.create_button("Traversal", self.show_traversal_options, 0)
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

    def show_traversal_options(self):
        if not self.tree_getter():
            messagebox.showwarning("Warning", "Please create or load a tree first.")
            return

        if self.popup:
            try:
                if not self.popup.winfo_exists():
                    self.popup = None
                else:
                    return
            except:
                self.popup = None

        self.popup = tk.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.config(bg="#f0f0f0")
        self.popup.protocol("WM_DELETE_WINDOW", self.clear_popup_and_destroy)

        self.update_idletasks()
        width = self.winfo_width()
        height = 210
        x = self.winfo_rootx()
        final_y = self.winfo_rooty() - height
        start_y = self.winfo_rooty() + self.winfo_height()
        self.popup.geometry(f"{width}x{height}+{x}+{start_y}")

        close_btn = tk.Label(self.popup, text="✖", font=("Arial", 12, "bold"),
                             bg="#f0f0f0", fg="black", cursor="hand2")
        close_btn.place(relx=1.0, x=-10, y=10, anchor="ne")
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#e0e0e0"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#f0f0f0"))
        close_btn.bind("<Button-1>", lambda e: self.clear_popup_and_destroy())

        button_frame = tk.Frame(self.popup, bg="#f0f0f0")
        button_frame.pack(pady=(20, 5), fill="x", expand=True)

        def create_option_button(label, mode):
            btn = tk.Label(button_frame, text=label, font=("Arial", 14), bg="#4CAF50", fg="white",
                           padx=20, pady=10, cursor="hand2", width=15)
            btn.pack(side="left", expand=True, padx=10, fill="x")
            btn.bind("<Enter>", lambda e: btn.config(bg="#45a049"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#4CAF50"))
            btn.bind("<Button-1>", lambda e: [self.set_traversal_mode_and_start(mode)])
            return btn

        create_option_button("Preorder", "preorder")
        create_option_button("Inorder", "inorder")
        create_option_button("Postorder", "postorder")

        text_frame = tk.Frame(self.popup, bg="#f0f0f0")
        text_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.output_display = tk.Text(text_frame, height=3, font=("Arial", 12), bg="#ffffff",
                                      wrap="word", relief="solid")
        self.output_display.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.output_display.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_display.config(yscrollcommand=scrollbar.set)
        self.output_display.insert("1.0", "Traversal result: ")
        self.output_display.config(state="disabled")

        def animate_slide(current_y):
            if current_y <= final_y:
                self.popup.geometry(f"{width}x{height}+{x}+{final_y}")
                return
            self.popup.geometry(f"{width}x{height}+{x}+{current_y}")
            self.popup.after(10, lambda: animate_slide(current_y - 10))

        animate_slide(start_y)

    def clear_popup_and_destroy(self):
        try:
            if self.popup and self.popup.winfo_exists():
                self.popup.destroy()
        except:
            pass
        self.popup = None

    def set_traversal_mode_and_start(self, mode):
        self.traversal_mode = mode
        self.start_traversal()
    def start_traversal(self):
        root = self.tree_getter()
        if not root:
            return

        if self.traversal_mode == "preorder":
            self.traversal_nodes = self.get_preorder_list(root)
        elif self.traversal_mode == "inorder":
            self.traversal_nodes = self.get_inorder_list(root)
        elif self.traversal_mode == "postorder":
            self.traversal_nodes = self.get_postorder_list(root)
        else:
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
        self.update_output_display(-1)

    def next_step(self):
        if not self.traversal_nodes or self.traversal_index >= len(self.traversal_nodes):
            return
        node = self.traversal_nodes[self.traversal_index]
        self.visualizer.highlighted_node = node
        self.visualizer.scroll_to_node(node)

        self.visualizer.update_highlight()
        self.node_label.config(text=f"Node: {node.val}")
        self.traversal_index += 1
        self.update_output_display(self.traversal_index - 1)
        self.progress_var.set((self.traversal_index / len(self.traversal_nodes)) * 100)


    def update_output_display(self, highlight_index):
        if not self.popup or not hasattr(self, 'output_display'):
            return

        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert("1.0", "Traversal result: ")

        for i, node in enumerate(self.traversal_nodes[:self.traversal_index]):
            self.output_display.insert(tk.END, f"{node.val}")
            if i < self.traversal_index - 1:
                self.output_display.insert(tk.END, " -> ")

        # In đậm node hiện tại
        if highlight_index >= 0 and highlight_index < len(self.traversal_nodes):
            start = len("Traversal result: ") + sum(len(str(n.val)) + 4 for n in self.traversal_nodes[:highlight_index])
            end = start + len(str(self.traversal_nodes[highlight_index].val))
            self.output_display.tag_add("bold", f"1.{start}", f"1.{end}")
            self.output_display.tag_config("bold", font=("Arial", 12, "bold"))

        self.output_display.see("end")
        self.output_display.config(state="disabled")

    def run_traversal(self):
        while self.traversing and self.traversal_index < len(self.traversal_nodes):
            if not self.paused:
                node = self.traversal_nodes[self.traversal_index]
                self.visualizer.highlighted_node = node
                self.visualizer.draw_tree(self.tree_getter())
                self.node_label.config(text=f"Node: {node.val}")
                self.traversal_index += 1
                self.update_output_display(self.traversal_index - 1)
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

    def get_preorder_list(self, root):
        if root is None:
            return []
        return [root] + self.get_preorder_list(root.left) + self.get_preorder_list(root.right)

    def get_inorder_list(self, root):
        if root is None:
            return []
        return self.get_inorder_list(root.left) + [root] + self.get_inorder_list(root.right)

    def get_postorder_list(self, root):
        if root is None:
            return []
        return self.get_postorder_list(root.left) + self.get_postorder_list(root.right) + [root]