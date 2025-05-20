import tkinter as tk
from tkinter import ttk, messagebox

class TraversalBar(tk.Frame):
    def __init__(self, parent, visualizer, tree_getter):
        super().__init__(parent, bg="grey")
        self.visualizer = visualizer
        self.tree_getter = tree_getter
        self.parent = parent
        self.pack(side="bottom", fill="x")

        self.traversal_nodes = []
        self.traversal_index = 0
        self.traversing = False
        self.paused = False
        self.traversal_mode = "bfs"
        self.result_popup = None
        self.option_popup = None

        self.grid_columnconfigure(4, weight=1)

        # Buttons
        self.traversal_btn = self.create_button("Traversal", self.show_option_popup, 0)
        self.pause_btn = self.create_button("Pause", self.toggle_pause_resume, 1)
        self.next_btn = self.create_button("Next", self.next_step, 2)
        self.stop_btn = self.create_button("Stop", self.stop_traversal, 3)

        # Progress bar (chiếm phần còn lại)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=4, sticky="we", padx=(10, 5))

        self.node_label = tk.Label(self, text="Node: -", font=("Arial", 12), bg="grey")
        self.node_label.grid(row=0, column=5, padx=5)

        tk.Label(self, text="Speed:", bg="grey", font=("Arial", 12)).grid(row=0, column=6, padx=(10, 0))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(self, from_=0.1, to=2.0, resolution=0.1,
                                    orient="horizontal", variable=self.speed_var, length=100)
        self.speed_scale.grid(row=0, column=7, padx=(0, 10))

    def create_button(self, text, command, col):
        btn = tk.Label(self, text=text, font=("Arial", 12), bg="white", fg="black",
                       padx=10, pady=3, cursor="hand2", relief="flat", bd=0)
        btn.grid(row=0, column=col, padx=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="white"))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def show_option_popup(self):
        if not self.tree_getter():
            messagebox.showwarning("Warning", "Please create or load a tree first.")
            return

        self.hide_result_popup()

        if self.option_popup and self.option_popup.winfo_exists():
            return

        self.option_popup = tk.Toplevel(self)
        self.option_popup.overrideredirect(True)
        self.option_popup.attributes("-topmost", True)
        self.option_popup.config(bg="#f9f9f9", bd=1, highlightthickness=1, highlightbackground="#ccc")

        # Lấy kích thước và vị trí nút Traversal
        self.update_idletasks()
        btn_x = self.traversal_btn.winfo_rootx()
        btn_y = self.traversal_btn.winfo_rooty()
        btn_width = self.traversal_btn.winfo_width()
        popup_width = btn_width
        popup_height = 160

        # Đặt popup ngay trên nút Traversal
        self.option_popup.geometry(f"{popup_width}x{popup_height}+{btn_x}+{btn_y - popup_height - 5}")

        # Frame chứa các lựa chọn
        frame = tk.Frame(self.option_popup, bg="#f9f9f9")
        frame.pack(fill="both", expand=True, pady=5)

        options = [("Preorder", "preorder"), ("Inorder", "inorder"),
                ("Postorder", "postorder"), ("BFS", "bfs")]

        for label, mode in options:
            btn = tk.Label(frame, text=label, font=("Arial", 11), bg="white", fg="black",
                        relief="solid", bd=1, padx=4, pady=6, width=popup_width//10, cursor="hand2")
            btn.pack(fill="x", padx=5, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="white"))
            btn.bind("<Button-1>", lambda e, m=mode: self.set_mode_and_start(m))





    def set_mode_and_start(self, mode):
        self.traversal_mode = mode
        if self.option_popup and self.option_popup.winfo_exists():
            self.option_popup.destroy()
        self.option_popup = None
        self.start_traversal()

    def start_traversal(self):
        root = self.tree_getter()
        if not root:
            return

        self.traversal_nodes = {
            "preorder": self.get_preorder_list,
            "inorder": self.get_inorder_list,
            "postorder": self.get_postorder_list,
            "bfs": self.get_bfs_list,
        }.get(self.traversal_mode, self.get_bfs_list)(root)

        self.traversal_index = 0
        self.traversing = True
        self.paused = False
        self.pause_btn.config(text="Pause")

        self.show_result_popup()
        self._traversal_step()

    def show_result_popup(self):
        if self.result_popup and self.result_popup.winfo_exists():
            self.result_popup.destroy()

        self.result_popup = tk.Toplevel(self)
        self.result_popup.overrideredirect(True)
        self.result_popup.config(bg="white")
        self.result_popup.attributes("-topmost", True)

        width = self.winfo_width()
        height = 60  # cao hơn tí cho đủ tag in đậm
        x = self.winfo_rootx()
        y = self.winfo_rooty() - height - 1
        self.result_popup.geometry(f"{width}x{height}+{x}+{y}")

        container = tk.Frame(self.result_popup, bg="white")
        container.pack(fill="both", expand=True)

        # Nút đóng X
        close_btn = tk.Label(container, text="✖", font=("Arial", 12, "bold"),
                            bg="white", fg="black", cursor="hand2")
        close_btn.pack(side="right", anchor="ne", padx=10, pady=5)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#e0e0e0"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="white"))
        close_btn.bind("<Button-1>", lambda e: self.result_popup.destroy())

        # Khung text
        self.output_display = tk.Text(container, height=2, font=("Arial", 12),
                                    bg="white", wrap="word", relief="flat", bd=0)
        self.output_display.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        self.output_display.insert("1.0", "Traversal result: ")
        self.output_display.config(state="disabled")



    def hide_result_popup(self):
        if self.result_popup and self.result_popup.winfo_exists():
            self.result_popup.destroy()
            self.result_popup = None

    def update_result_display(self):
        if not self.result_popup or not hasattr(self, 'output_display'):
            return

        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert("1.0", "Traversal result: ")

        base_len = len("Traversal result: ")
        for i, node in enumerate(self.traversal_nodes[:self.traversal_index]):
            node_str = str(node.val)
            self.output_display.insert(tk.END, node_str)

            if i == self.traversal_index - 1:
                start = base_len
                end = start + len(node_str)
                self.output_display.tag_add("bold", f"1.{start}", f"1.{end}")
                self.output_display.tag_config("bold", font=("Arial", 12, "bold"))

            base_len += len(node_str)
            if i < self.traversal_index - 1:
                self.output_display.insert(tk.END, " -> ")
                base_len += 4

        self.output_display.config(state="disabled")





    def _traversal_step(self):
        if not self.traversing or self.traversal_index >= len(self.traversal_nodes):
            self.traversing = False
            self.pause_btn.config(text="Pause")
            return

        if not self.paused:
            node = self.traversal_nodes[self.traversal_index]
            self.visualizer.highlighted_node = node
            self.visualizer.draw_tree(self.tree_getter())
            self.node_label.config(text=f"Node: {node.val}")
            self.traversal_index += 1
            self.progress_var.set((self.traversal_index / len(self.traversal_nodes)) * 100)
            self.update_result_display()

        delay = int(1000 / self.speed_var.get())
        self.after(delay, self._traversal_step)

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
        self.hide_result_popup()

    def next_step(self):
        if not self.traversal_nodes or self.traversal_index >= len(self.traversal_nodes):
            return
        node = self.traversal_nodes[self.traversal_index]
        self.visualizer.highlighted_node = node
        self.visualizer.draw_tree(self.tree_getter())
        self.node_label.config(text=f"Node: {node.val}")
        self.traversal_index += 1
        self.progress_var.set((self.traversal_index / len(self.traversal_nodes)) * 100)
        self.update_result_display()

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
        if not root:
            return []
        return [root] + self.get_preorder_list(root.left) + self.get_preorder_list(root.right)

    def get_inorder_list(self, root):
        if not root:
            return []
        return self.get_inorder_list(root.left) + [root] + self.get_inorder_list(root.right)

    def get_postorder_list(self, root):
        if not root:
            return []
        return self.get_postorder_list(root.left) + self.get_postorder_list(root.right) + [root]
