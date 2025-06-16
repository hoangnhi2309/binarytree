import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename, askopenfilename
import random
import ast
from tkinter import simpledialog

class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None
        self.height = 1 

class BinaryTreeVisualizer:
    def __init__(self, canvas):
        self.tree_root = None
        self.controller = None
        self.canvas = canvas
        self.node_radius = 18 
        self.level_height = 60
        self.highlighted_node = None  
        self.nodes_positions = [] 
        self.root = None
        self.sidebar = None
        self.zoom = 1.0  # Tỉ lệ zoom mặc định
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows, Mac (cuộn)
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Một số Linux/Mac cuộn lên
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Một số Linux/Mac cuộn xuống
    def set_controller(self, controller):
        self.controller = controller

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root
    def bind_click_event(self):
        # Chuột trái: chọn node (highlight)
        self.canvas.bind("<Button-1>", self.on_canvas_left_click)
        # Chuột phải: mở menu node (Windows/Linux/Mac)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<Button-2>", self.on_canvas_right_click)  # Mac

    def on_canvas_left_click_show_menu(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                return

        # Không làm gì nếu không nhấn vào node


    def on_canvas_left_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.highlighted_node = node
                self.draw_tree(self.root)
                return
        self.highlighted_node = None
        self.draw_tree(self.root)
    def on_canvas_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                return
    def on_canvas_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                return
        # Nếu không bấm vào node nào thì hiện menu canvas
        self.show_canvas_menu(event)

    def on_canvas_middle_click(self, event):
        pass

    def show_node_menu(self, event, node):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node(node))
        menu.add_command(label="Delete Node", command=lambda: self.delete_node(node))

        add_menu = tk.Menu(menu, tearoff=0)
        # Disable nếu đã có node trái/phải
        if node.left is not None:
            add_menu.add_command(label="Left side", state="disabled")
        else:
            add_menu.add_command(label="Left side", command=lambda: self.add_child_node(node, "left"))
        if node.right is not None:
            add_menu.add_command(label="Right side", state="disabled")
        else:
            add_menu.add_command(label="Right side", command=lambda: self.add_child_node(node, "right"))
        menu.add_cascade(label="Add Node", menu=add_menu)

        # Chỉ thêm "Switch Node" nếu là BinaryTreeVisualizer thường
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer
        if not isinstance(self, (BSTVisualizer, AVLVisualizer)):
            menu.add_command(label="Switch Node", command=lambda: self.switch_node(node))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []

        if root:
            max_depth = self.get_tree_depth(root)

            # Import để kiểm tra loại cây
            from visualizer.bst_visualizer import BSTVisualizer
            from visualizer.avl_visualizer import AVLVisualizer

            # Tính số node ở tầng cuối
            if isinstance(self, BSTVisualizer) and not isinstance(self, AVLVisualizer):
                def count_last_level_nodes(node, depth, max_depth):
                    if not node:
                        return 0
                    if depth == max_depth:
                        return 1
                    return count_last_level_nodes(node.left, depth + 1, max_depth) + \
                        count_last_level_nodes(node.right, depth + 1, max_depth)

                actual_nodes_last_level = count_last_level_nodes(root, 1, max_depth)
                min_nodes_last_level = max(2, 2 ** (max_depth - 3))
                max_nodes_last_level = max(actual_nodes_last_level, min_nodes_last_level)
            else:
                max_nodes_last_level = 2 ** (max_depth - 1)

            # Tính khoảng cách giữa các node (adaptive gap)
            min_gap = 30 * self.zoom
            max_gap = 80 * self.zoom
            # Tự động điều chỉnh khoảng cách dựa theo số node ở tầng cuối
            gap = max(min_gap, min(max_gap, (600 * self.zoom) / max_nodes_last_level))

            total_width = max_nodes_last_level * gap
            est_canvas_width = max(1000, int(total_width + 2 * self.node_radius * self.zoom))
            est_canvas_height = int((max_depth + 1) * self.level_height * self.zoom + 100)
            self.canvas.config(scrollregion=(0, 0, est_canvas_width, est_canvas_height))

            start_x = est_canvas_width // 2
            start_y = 40 * self.zoom
            x_offset = total_width // 2

            self._draw_subtree(root, start_x, start_y, x_offset, 0)

        # Căn giữa lại canvas sau khi vẽ
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=bbox)

            canvas_width = bbox[2] - bbox[0]
            visible_width = self.canvas.winfo_width()
            x = max((canvas_width - visible_width) // 2, 0)
            self.canvas.xview_moveto(x / canvas_width if canvas_width else 0)

            canvas_height = bbox[3] - bbox[1]
            visible_height = self.canvas.winfo_height()
            y = max((canvas_height - visible_height) // 2, 0)
            self.canvas.yview_moveto(y / canvas_height if canvas_height else 0)

    def _draw_subtree(self, node, x, y, x_offset, depth):
        min_offset = 20 * self.zoom  # đảm bảo node không dính nhau

        if node.left:
            next_offset = max(x_offset // 2, min_offset)
            left_x = x - x_offset
            left_y = y + self.level_height * self.zoom
            self.canvas.create_line(x, y, left_x, left_y)
            self._draw_subtree(node.left, left_x, left_y, next_offset, depth + 1)

        if node.right:
            next_offset = max(x_offset // 2, min_offset)
            right_x = x + x_offset
            right_y = y + self.level_height * self.zoom
            self.canvas.create_line(x, y, right_x, right_y)
            self._draw_subtree(node.right, right_x, right_y, next_offset, depth + 1)

        radius = self.node_radius * self.zoom
        color = "grey" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", int(12 * self.zoom), "bold"))
        self.nodes_positions.append((x, y, node))


    def get_tree_depth(self, node):
        if not node:
            return 0
        return 1 + max(self.get_tree_depth(node.left), self.get_tree_depth(node.right))

    def scroll_to_node(self, node):

        if not node or not hasattr(node, 'canvas_x') or not hasattr(node, 'canvas_y'):
            return
        # Giả sử node.canvas_x, node.canvas_y là tọa độ node trên canvas
        canvas = self.canvas
        canvas_width = int(canvas.cget("width"))
        canvas_height = int(canvas.cget("height"))
        x = max(node.canvas_x - canvas_width // 2, 0)
        y = max(node.canvas_y - canvas_height // 2, 0)
        canvas.xview_moveto(x / canvas.bbox("all")[2])
        canvas.yview_moveto(y / canvas.bbox("all")[3])

        for x, y, n in self.nodes_positions:
            if n == node:
                # Kích thước vùng vẽ (toàn bộ canvas)
                bbox = self.canvas.bbox("all")
                if not bbox:
                    return
                total_width = bbox[2]
                total_height = bbox[3]

                # Kích thước hiển thị canvas
                visible_width = self.canvas.winfo_width()
                visible_height = self.canvas.winfo_height()

                # Tính vị trí muốn scroll tới (đưa node ra giữa)
                x_target = max(min(x - visible_width // 2, total_width - visible_width), 0)
                y_target = max(min(y - visible_height // 2, total_height - visible_height), 0)

                # Scroll theo tỷ lệ (0.0 -> 1.0)
                self.canvas.xview_moveto(x_target / total_width)
                self.canvas.yview_moveto(y_target / total_height)

                break

    def tree_to_array(self, root):
        result = []
        queue = [root]
        while queue:
            node = queue.pop(0)
            if node:
                result.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append(0)
        # Đảm bảo không xóa các số 0 cuối nếu muốn giữ nguyên cấu trúc
        return result


    def edit_node(self, node):
        popup = tk.Toplevel(self.canvas)
        popup.title("Edit Node")
        popup.geometry("300x150")
        popup.transient(self.canvas.winfo_toplevel())

        # Center the popup
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        popup.geometry(f"+{x}+{y}")

        # Label New Value (căn trái)
        label = tk.Label(popup, text=f"Edit node {node.val} to:", font=("Arial", 13), anchor="w")
        label.pack(fill="x", padx=20, pady=(18, 2))

        # Entry New Value
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 5))
        value_entry.focus_set()

        # Label báo lỗi màu đỏ
        error_label = tk.Label(popup, text="", fg="red", font=("Arial", 11))
        error_label.pack(fill="x", padx=10, pady=(0, 5))

        # Frame chứa nút Edit và Cancel căn phải
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(button_frame).pack(side="left", expand=True)

        def on_enter(e):
            e.widget.config(bg="#lightblue", fg="black")
        def on_leave(e):
            e.widget.config(bg="grey")
        cancel_button = tk.Button(button_frame, text="Cancel", command=popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        cancel_button.bind("<Enter>", on_enter)
        cancel_button.bind("<Leave>", on_leave)
        def save_value():
            try:
                new_value = int(value_entry.get())
                if new_value == node.val:
                    popup.destroy()
                    return
                # Không cho trùng giá trị với bất kỳ node nào khác
                if self.value_exists(self.root, new_value) and new_value != node.val:
                    error_label.config(text=f"The value {new_value} already exists in the tree.")
                    return
                node.val = new_value
                self.draw_tree(self.root)
                if self.sidebar:
                    new_array = self.tree_to_array(self.root)
                    self.sidebar.array = new_array
                    self.sidebar.update_array_display(new_array)
                popup.destroy()
            except ValueError:
                error_label.config(text="Please enter a valid integer.")

        save_button = tk.Button(button_frame, text="Edit", command=save_value, font=("Arial", 12), bg="grey")
        save_button.pack(side="right", padx=(5, 0))
        save_button.bind("<Enter>", on_enter)
        save_button.bind("<Leave>", on_leave)
        # Bind Enter key to save_value function
        value_entry.bind("<Return>", lambda e: save_value())


    def delete_node(self, node):
        def remove_node(parent, target):
            if parent.left == target:
                parent.left = None
            elif parent.right == target:
                parent.right = None

        def find_and_remove(parent, current, target):
            if current is None:
                return
            if current == target:
                remove_node(parent, target)
                return
            find_and_remove(current, current.left, target)
            find_and_remove(current, current.right, target)

        if self.root == node:
            self.root = None
        else:
            find_and_remove(None, self.root, node)

        self.draw_tree(self.root)
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def value_exists(self, node, val):
        if node is None:
            return False
        if node.val == val:
            return True
        return self.value_exists(node.left, val) or self.value_exists(node.right, val)


    def is_valid_insert(self, parent, val, is_left):
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer

        # Ngăn giá trị trùng cho mọi loại cây
        if self.value_exists(self.root, val):
            messagebox.showwarning("Duplicate Value", f"The value {val} already exists in the tree.")
            return False

        # Nếu là BST hoặc AVL thì kiểm tra hướng hợp lệ
        if isinstance(self, (BSTVisualizer, AVLVisualizer)):
            if is_left and val >= parent.val:
                messagebox.showwarning("Invalid Position", f"The value {val} must be less than {parent.val} to insert on the left.")
                return False
            if not is_left and val <= parent.val:
                messagebox.showwarning("Invalid Position", f"The value {val} must be greater than {parent.val} to insert on the right.")
                return False

        return True

    def add_child_node(self, node, direction):
        if direction == "left" and node.left is not None:
            messagebox.showwarning("Node Exists", "Left node already exists.")
            return
        if direction == "right" and node.right is not None:
            messagebox.showwarning("Node Exists", "Right node already exists.")
            return

        popup = tk.Toplevel(self.canvas)
        popup.title(f"Add {direction.capitalize()} Child Node")
        popup.geometry("300x130")
        popup.transient(self.canvas.winfo_toplevel())

        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="New Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(15, 2))
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 15))
        value_entry.focus_set()

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(button_frame).pack(side="left", expand=True)

        tk.Button(button_frame, text="Cancel", command=popup.destroy,
                font=("Arial", 12), bg="grey", fg="black").pack(side="right", padx=(0, 5))

        def on_add():
            val = value_entry.get()
            try:
                new_value = int(val)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid integer value.")
                return

            is_left = direction == "left"
            if not self.is_valid_insert(node, new_value, is_left):
                return

            new_node = TreeNode(new_value)
            if is_left:
                node.left = new_node
            else:
                node.right = new_node

            popup.destroy()
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)

        tk.Button(button_frame, text="Add", command=on_add,
                font=("Arial", 12), bg="grey").pack(side="right", padx=(5, 0))
        value_entry.bind("<Return>", lambda e: on_add())

    def switch_all_nodes_with_two_children(self):
        def dfs(node):
            if node is None:
                return
            # Nếu node có đủ cả trái và phải, thì hoán đổi
            if node.left is not None and node.right is not None:
                node.left, node.right = node.right, node.left
            # Đệ quy tiếp các node con
            dfs(node.left)
            dfs(node.right)

        if self.root is None:
            self.show_toast_notification("The tree is empty.", bg_color="lightcoral")
            return

        dfs(self.root)  # Duyệt cây từ root

        self.highlighted_node = None
        self.switching_node = None
        self.draw_tree(self.root)

        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

        self.show_toast_notification("Switched all nodes with two children successfully!", bg_color="lightgreen")

    def show_canvas_menu(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Find node", command=self.on_find_node)
        menu.add_command(label="Create random tree", command=self.on_random_tree) 
        menu.add_command(label="Delete tree", command=self.on_clear_tree)
        menu.add_command(label="Save to file", command=self.save_tree_to_file)
        menu.add_command(label="Load from file", command=self.load_tree_from_file)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_random_tree(self):
        self.popup = tk.Toplevel(self.canvas.winfo_toplevel())
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.canvas.winfo_toplevel())

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
        from visualizer.avl_visualizer import AVLVisualizer

        if isinstance(self, BinaryTreeVisualizer) and not isinstance(self, (BSTVisualizer, AVLVisualizer)):
            label_text = "Tree Depth:"
            default_value = "3"
            tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
            # Label cảnh báo
            self.depth_warning_label = tk.Label(self.popup, text="", fg="red", font=("Arial", 10))
            self.depth_warning_label.pack(fill="x", padx=10, pady=(0, 2))
            # Entry có validate
            def validate_depth(new_value):
                if not new_value:
                    self.depth_warning_label.config(text="")
                    return True
                try:
                    v = int(new_value)
                    if 1 <= v <= 7:
                        self.depth_warning_label.config(text="")
                        return True
                    else:
                        self.depth_warning_label.config(text="Depth must be from 1 to 7.")
                        return False
                except ValueError:
                    self.depth_warning_label.config(text="Depth must be an integer.")
                    return False
            vcmd = (self.popup.register(validate_depth), '%P')
            self.depth_entry = tk.Entry(self.popup, font=("Arial", 12), validate="key", validatecommand=vcmd)
            self.depth_entry.insert(0, default_value)
            self.depth_entry.pack(fill="x", padx=10, pady=(0, 10))
        else:
            label_text = "Number of Nodes:"
            default_value = "10"
            tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
            self.depth_entry = tk.Entry(self.popup, font=("Arial", 12))
            self.depth_entry.insert(0, default_value)
            self.depth_entry.pack(fill="x", padx=10, pady=(0, 10))

        button_frame = tk.Frame(self.popup)
        button_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(button_frame).pack(side="left", expand=True)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        create_button = tk.Button(button_frame, text="Create", command=self.create_tree_and_close, font=("Arial", 12), bg="grey")
        create_button.pack(side="right", padx=(5, 0))

        # --- BIND ENTER CHO TẤT CẢ ENTRY ---
        for entry in [self.min_entry, self.max_entry, self.depth_entry]:
            entry.bind("<Return>", lambda e: self.create_tree_and_close())
    def create_tree_and_close(self):
        try:
            min_value = int(self.min_entry.get())
            max_value = int(self.max_entry.get())
            depth = int(self.depth_entry.get())

            MAX_DEPTH = 7  # Giới hạn độ sâu tối đa
            MIN_DEPTH = 1  # Giới hạn độ sâu tối thiểu

            if depth > MAX_DEPTH:
                messagebox.showwarning("Depth too large", f"Max allowed depth is {MAX_DEPTH}.")
                return

            if depth < MIN_DEPTH:
                messagebox.showwarning("Depth too small", f"Depth must be at least {MIN_DEPTH}.")
                return

            if min_value >= max_value:
                messagebox.showwarning("Invalid Input", "Min value must be less than Max value.")
                return

            max_nodes = 2**depth - 1
            available_values = max_value - min_value + 1

            if max_nodes > available_values:
                messagebox.showwarning(
                    "Invalid Input",
                    f"Not enough unique values to fill the tree.\n"
                    f"Required: {max_nodes}, Available: {available_values}.\n"
                    f"Increase the range (Min/Max) or reduce the depth."
                )
                return


            arr = self.generate_random_tree_array(min_value, max_value, depth)
            tree_root = self.array_to_tree_level_order(arr)
            self.root = tree_root
            self.last_created_array = arr[:]  # <-- Lưu lại mảng gốc
            self.draw_tree(self.root)

            if tree_root:
                self.root = tree_root
                self.draw_tree(self.root)
                if self.sidebar:
                    new_array = self.tree_to_array(self.root)
                    self.sidebar.array = new_array
                    self.sidebar.update_array_display(new_array)
            else:
                messagebox.showwarning("Error", "Failed to create tree.")

            self.popup.destroy()

        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid integers for Min, Max, and Depth.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def array_to_tree_level_order(self, arr):
        if not arr:
            return None
        nodes = [TreeNode(val) if val != 0 else None for val in arr]
        kids = nodes[::-1]
        root = kids.pop()
        for node in nodes:
            if node:
                if kids: node.left = kids.pop()
                if kids: node.right = kids.pop()
        return root
    def generate_random_tree_array(self, min_value, max_value, depth):
        import random

        max_nodes = 2 ** depth - 1
        all_values = list(range(min_value, max_value + 1))

        if len(all_values) < 2:
            raise ValueError("Khoảng giá trị quá hẹp để có cả min và max.")

        if max_nodes < 2:
            raise ValueError("Cần ít nhất 2 node để chứa min và max.")

        num_real_nodes = random.randint(2, max_nodes)
        if num_real_nodes < 2:
            raise ValueError("Không đủ node để chứa min và max.")

        # Chọn giá trị (bao gồm min, max và các node ngẫu nhiên)
        remaining = list(set(all_values) - {min_value, max_value})
        if len(remaining) >= (num_real_nodes - 2):
            sampled = random.sample(remaining, num_real_nodes - 2)
        else:
            sampled = random.choices(remaining, k=num_real_nodes - 2)

        values = [min_value, max_value] + sampled
        random.shuffle(values)

        # Tạo mảng cây theo dạng BFS
        tree = []
        queue = [0]  # dùng chỉ số
        val_index = 0

        while queue and val_index < len(values):
            idx = queue.pop(0)
            if idx >= max_nodes:
                break
            # Đảm bảo mảng có đủ chỗ
            while len(tree) <= idx:
                tree.append(0)
            # Gán giá trị thật
            tree[idx] = values[val_index]
            val_index += 1
            # Nếu không phải node rỗng thì cho phép có con
            if tree[idx] != 0:
                queue.append(2 * idx + 1)
                queue.append(2 * idx + 2)

        # Đảm bảo mảng đủ kích thước theo depth
        while len(tree) < max_nodes:
            tree.append(0)

        return tree



    def update_max_depth_hint(self):
        try:
            min_value = int(self.min_entry.get())
            max_value = int(self.max_entry.get())
            available_values = max_value - min_value + 1

            # Tính độ sâu tối đa có thể
            max_depth = 0
            while (2**max_depth - 1) <= available_values:
                max_depth += 1
            max_depth -= 1

            # Hiển thị gợi ý ra label (không ép người dùng)
            self.depth_hint_label.config(text=f"Suggested max depth: {max_depth}")
        except ValueError:
            self.depth_hint_label.config(text="")

    def on_clear_tree(self):
        self.root = None
        self.draw_tree(self.root)
        if self.sidebar:
            self.sidebar.array = []
            self.sidebar.update_array_display([])

    def on_find_node(self):
        # Popup nhỏ style giống edit/add, căn giữa màn hình
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Find Node")
        popup.geometry("300x140")
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center the popup
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        popup.geometry(f"+{x}+{y}")
        
        tk.Label(popup, text="Enter node value to find:", font=("Arial", 12),anchor="w").pack(fill="x", padx=10, pady=(15, 5))
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 10))
        value_entry.focus_set()

        # Label cảnh báo
        warning_label = tk.Label(popup, text="", fg="red", font=("Arial", 10))
        warning_label.pack(fill="x", padx=10, pady=(0, 2))

        def do_find():
            val = value_entry.get()
            try:
                value = int(val)
            except ValueError:
                warning_label.config(text="Please enter a valid integer.")
                return
            # Tìm node theo giá trị (DFS)
            def find_node(root, v):
                if not root:
                    return None
                if root.val == v:
                    return root
                left = find_node(root.left, v)
                if left:
                    return left
                return find_node(root.right, v)
            found_node = find_node(self.root, value)
            if found_node:
                self.highlighted_node = found_node
                self.draw_tree(self.root)
                self.scroll_to_node(found_node)
                if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                    self.sidebar.show_toast_notification(f"Found node {value}.")
                popup.destroy()
            else:
                warning_label.config(text=f"No valid node found {value}.")

        # Frame chứa nút Find và Cancel căn phải
        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))
        tk.Label(button_frame).pack(side="left", expand=True)
        cancel_button = tk.Button(button_frame, text="Cancel", command=popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        find_button = tk.Button(button_frame, text="Find", font=("Arial", 12), command=do_find, bg="grey")
        find_button.pack(side="right", padx=(5, 0))
        value_entry.bind("<Return>", lambda e: do_find())

    def find_node_by_value(self, node, value):
        if node is None:
            return None
        if node.val == value:
            return node
        left = self.find_node_by_value(node.left, value)
        if left:
            return left
        return self.find_node_by_value(node.right, value)
    def save_tree_to_file(self):
        if not self.root:
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                self.sidebar.show_toast_notification("No tree to save.")
            else:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("No Tree", "There is no tree to save.")
            return

        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Tree As"
        )
        if not file_path:
            return

        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer
        if not isinstance(self, (BSTVisualizer, AVLVisualizer)):
            result = []
            def dfs(node):
                if not node:
                    return
                left_val = node.left.val if node.left else 0
                right_val = node.right.val if node.right else 0
                result.append(f"{node.val}, {left_val}, {right_val}")
                dfs(node.left)
                dfs(node.right)
            dfs(self.root)
            content = "\n".join(result)
        else:
            array = self.tree_to_array(self.root)
            filtered = [str(v) for v in array if v != 0]
            content = ", ".join(filtered)

        try:
            with open(file_path, "w") as f:
                f.write(content)
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                self.sidebar.show_toast_notification("Tree successfully saved to \n" + file_path)
            else:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Save", f"Tree successfully saved to \n{file_path}")
        except Exception as e:
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                self.sidebar.show_toast_notification(f"Error saving file \n{e}")
            else:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", f"Error saving file \n{e}")
    def load_tree_from_file(self):
        file_path = askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Open Tree File"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                content = f.read()

            from visualizer.bst_visualizer import BSTVisualizer
            from visualizer.avl_visualizer import AVLVisualizer

            # Nếu là BST/AVL: file là mảng giá trị
            if isinstance(self, (BSTVisualizer, AVLVisualizer)):
                # Hỗ trợ cả dạng "1,2,3" hoặc từng dòng một số
                if "," in content:
                    values = [int(v.strip()) for v in content.split(",") if v.strip()]
                else:
                    # Đọc values từ file
                    if "," in content:
                        values = [int(v.strip()) for v in content.split(",") if v.strip()]
                    else:
                        values = [int(line.strip()) for line in content.splitlines() if line.strip()]
                    root = None
                    for v in values:
                        root = self.insert_bst(root, v) if isinstance(self, BSTVisualizer) else self.insert_avl(root, v)
                    self.root = root
                    self.draw_tree(self.root)
                    if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                        arr = self.tree_to_array(self.root)
                        self.sidebar.update_array_display(arr)
                    self.show_toast_notification(f"Tree loaded from \n{file_path}")
                    return

            # Nếu là BinaryTree: file là từng dòng "node, left, right"
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            node_list = []
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                node_val = int(parts[0].strip())
                left_val = int(parts[1].strip())
                right_val = int(parts[2].strip())
                node_list.append((node_val, left_val, right_val))

            tree_nodes = [TreeNode(val) for val, _, _ in node_list]
            for idx, (val, l_val, r_val) in enumerate(node_list):
                node = tree_nodes[idx]
                # Gán left
                if l_val != 0:
                    # Tìm node con theo thứ tự xuất hiện đầu tiên chưa được gán làm con
                    for j, (v, _, _) in enumerate(node_list):
                        if v == l_val and tree_nodes[j] != node and not hasattr(tree_nodes[j], "_used_left"):
                            node.left = tree_nodes[j]
                            tree_nodes[j]._used_left = True
                            break
                # Gán right
                if r_val != 0:
                    for j, (v, _, _) in enumerate(node_list):
                        if v == r_val and tree_nodes[j] != node and not hasattr(tree_nodes[j], "_used_right"):
                            node.right = tree_nodes[j]
                            tree_nodes[j]._used_right = True
                            break

            root = tree_nodes[0] if tree_nodes else None
            self.tree_root = root
            self.root = root
            self.draw_tree(self.root)
            array_representation = self.tree_to_array(self.root)
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                self.sidebar.update_array_display(array_representation)
            self.show_toast_notification(f"Tree loaded from \n{file_path}")

        except Exception as e:
            self.show_toast_notification(f"Error loading file \n{e}")

    def create_random_binary_tree(self):
        # Gọi hàm create_random_tree của BinaryTreeVisualizer với tham số mặc định hoặc tự lấy từ UI nếu có
        # Ở đây giả sử gọi với min_val=1, max_val=99, num_nodes=10 tạm thời
        visualizer = BinaryTreeVisualizer(self.canvas)
        # Gọi hàm create_random_tree của BinaryTreeVisualizer, truyền tham số nếu cần
        tree_root = visualizer.create_random_tree(1, 99, 10)  
        if tree_root:
            self.set_root(tree_root)
            self.draw_tree(tree_root)

    def switch_node(self, node):
        if node is None:
            return
        node.left, node.right = node.right, node.left
        self.draw_tree(self.root)
        # Cập nhật array trên sidebar nếu có
        if hasattr(self, "sidebar") and hasattr(self.sidebar, "tree_to_array") and hasattr(self.sidebar, "update_array_display"):
            arr = self.sidebar.tree_to_array(self.root)
            self.sidebar.array = arr
            self.sidebar.update_array_display(arr)

    def zoom_in(self):
        self.zoom *= 1.1
        self.draw_tree(self.root)

    def zoom_out(self):
        if self.zoom > 0.5:  # hoặc 0.7More actions
            self.zoom /= 1.1
            self.draw_tree(self.root)

    def on_mousewheel(self, event):
        if hasattr(event, 'delta'):
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # MacOS
            if event.num == 4:
                self.zoom_in()
            elif event.num == 5:
                self.zoom_out()
    def update_edit(self, array_text):
        """
        Cập nhật lại cây từ array dạng val, left, right (mỗi dòng một node).
        array_text: chuỗi nhiều dòng, mỗi dòng: val, left, right
        """
        lines = [line.strip() for line in array_text.strip().split("\n") if line.strip()]
        node_map = {}
        for line in lines:
            parts = line.split(",")
            if len(parts) != 3:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", "Each line must have exactly 3 values: val, left, right.")
                return
            try:
                val = int(parts[0].strip())
                left = int(parts[1].strip())
                right = int(parts[2].strip())
                if val in node_map:
                    import tkinter.messagebox as messagebox
                    messagebox.showerror("Error", f"Node {val} duplicated.")
                    return
                node_map[val] = (left, right)
            except ValueError:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", "All values must be integers.")
                return

        if not node_map:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("Warning", "There is no data to update.")
            return

        # Tạo các node
        nodes = {}
        def get_node(val):
            if val == 0:
                return None
            if val not in nodes:
                nodes[val] = TreeNode(val)
            return nodes[val]

        for val, (l_val, r_val) in node_map.items():
            node = get_node(val)
            node.left = get_node(l_val)
            node.right = get_node(r_val)

        try:
            root_val = int(lines[0].split(",")[0].strip())
            root = get_node(root_val)
        except Exception:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", "Error determining root node.")
            return

        # Giữ lại các node còn liên kết từ root
        linked = set()
        def dfs(n):
            if n and n.val not in linked:
                linked.add(n.val)
                dfs(n.left)
                dfs(n.right)
        dfs(root)

        self.root = root
        self.draw_tree(root)
        # Nếu có sidebar, cập nhật lại array hiển thị
        if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
            arr = self.tree_to_array(root)
            self.sidebar.update_array_display(arr)