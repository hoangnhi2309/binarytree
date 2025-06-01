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
    def set_controller(self, controller):
        self.controller = controller

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root
    def bind_click_event(self):
        self.canvas.bind("<Button-1>", self.on_canvas_left_click_show_menu)   # Chuột trái: menu node
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)            # Chuột phải: menu canvas (Windows/Linux)
        self.canvas.bind("<Button-2>", self.on_canvas_right_click)            # Chuột phải: menu canvas (Mac)

    def on_canvas_left_click_show_menu(self, event):
        x, y = event.x, event.y
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                return
        # Không làm gì nếu không nhấn vào node

    def on_canvas_left_click(self, event):
        x, y = event.x, event.y
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.highlighted_node = node
                self.draw_tree(self.root)
                return
        self.highlighted_node = None
        self.draw_tree(self.root)

    def on_canvas_right_click(self, event):
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
            menu.add_command(label="Switch Node", command=lambda: self.switch_node(self.highlighted_node))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []

        if root:
            max_depth = self.get_tree_depth(root)
            canvas_width = max(800, int(2 ** max_depth * self.node_radius * 1.5 * self.zoom))
            start_x = canvas_width // 2
            canvas_height = int((max_depth + 1) * self.level_height * self.zoom + 100)
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

            start_x = canvas_width // 2
            x_offset = self.node_radius * (2 ** (max_depth - 1)) * 0.8 * self.zoom
            self._draw_subtree(root, start_x, 40 * self.zoom, x_offset, 0)

            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.config(scrollregion=bbox)

    def _draw_subtree(self, node, x, y, x_offset, depth):
        if node.left:
            left_x = x - x_offset
            left_y = y + self.level_height * self.zoom
            self.canvas.create_line(x, y, left_x, left_y)
            self._draw_subtree(node.left, left_x, left_y, x_offset // 2, depth + 1)

        if node.right:
            right_x = x + x_offset
            right_y = y + self.level_height * self.zoom
            self.canvas.create_line(x, y, right_x, right_y)
            self._draw_subtree(node.right, right_x, right_y, x_offset // 2, depth + 1)

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
        if not root:
            return []
        result = []
        queue = [root]
        while queue:
            current = queue.pop(0)
            if current:
                result.append(current.val)
                queue.append(current.left)
                queue.append(current.right)
            else:
                result.append(0)
        return result

    def edit_node(self, node):
        popup = tk.Toplevel(self.canvas)
        popup.title("Edit Node")
        popup.geometry("300x130")
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
        tk.Label(popup, text="New Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(15, 2))

        # Entry New Value (căn chỉnh giống on_random_tree)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 15))

        # Frame chứa nút Edit và Cancel căn phải
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10, padx=10, fill="x")

        # Spacer đẩy nút sang phải
        tk.Label(button_frame).pack(side="left", expand=True)

        # Nút Cancel
        cancel_button = tk.Button(button_frame, text="Cancel", command=popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))

        # Nút Edit (Save)
        save_button = tk.Button(button_frame, text="Edit", command=lambda: self.save_value(node, value_entry, popup), font=("Arial", 12), bg="grey")
        save_button.pack(side="right", padx=(5, 0))

    def save_value(self, node, value_entry, popup):
        try:
            new_value = int(value_entry.get())
            node.val = new_value
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)
            popup.destroy()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
            
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

    def add_child_node(self, node, direction):
        # Kiểm tra node trái hoặc phải đã tồn tại chưa
        if direction == "left" and node.left is not None:
            messagebox.showwarning("Node Exists", "Left node already exists.")
            return
        if direction == "right" and node.right is not None:
            messagebox.showwarning("Node Exists", "Right node already exists.")
            return

        # Tạo popup nhập giá trị node mới (Toplevel)
        popup = tk.Toplevel(self.canvas)
        popup.title(f"Add {direction.capitalize()} Child Node")
        popup.geometry("300x130")
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
        tk.Label(popup, text="New Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(15, 2))

        # Entry New Value
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 15))

        # Frame chứa nút Cancel và Add (Save)
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10, padx=10, fill="x")

        # Spacer đẩy nút sang phải
        tk.Label(button_frame).pack(side="left", expand=True)

        # Nút Cancel
        cancel_button = tk.Button(button_frame, text="Cancel", command=popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))

        # Hàm xử lý khi bấm nút Add
        def on_add():
            val = value_entry.get()
            try:
                new_value = int(val)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid integer value.")
                return
            new_node = TreeNode(new_value)
            if direction == "left":
                node.left = new_node
            else:  # direction == "right"
                node.right = new_node

            popup.destroy()  # Đóng popup
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)

        # Nút Add
        add_button = tk.Button(button_frame, text="Add", command=on_add, font=("Arial", 12), bg="grey")
        add_button.pack(side="right", padx=(5, 0))



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
        from components.sidebar import open_random_tree_popup
        open_random_tree_popup(self, mode="binary")

    def on_random_tree(self):
        self.popup = tk.Toplevel(self.canvas.winfo_toplevel())
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.canvas.winfo_toplevel())

        # Center the popup
        self.popup.update_idletasks()
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        popup_width = self.popup.winfo_width()
        popup_height = self.popup.winfo_height()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        self.popup.geometry(f"+{x}+{y}")

        # Min Value
        tk.Label(self.popup, text="Min Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.min_entry.insert(0, "1")
        self.min_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Max Value
        tk.Label(self.popup, text="Max Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.max_entry.insert(0, "99")
        self.max_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Tree Depth
        tk.Label(self.popup, text="Tree Depth:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.depth_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.depth_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.depth_entry.insert(0, "3")

        # Frame chứa 2 nút Create và Cancel căn phải
        button_frame = tk.Frame(self.popup)
        button_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(button_frame).pack(side="left", expand=True)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        create_button = tk.Button(button_frame, text="Create", command=self.create_tree_and_close, font=("Arial", 12), bg="grey")
        create_button.pack(side="right", padx=(5, 0))

        self.min_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())
        self.max_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())
        self.update_max_depth_hint()

    def create_tree_and_close(self):
        try:
            min_value = int(self.min_entry.get())
            max_value = int(self.max_entry.get())
            depth = int(self.depth_entry.get())

            if min_value >= max_value:
                messagebox.showwarning("Invalid Input", "Min value must be less than Max value.")
                return
            if depth <= 0:
                messagebox.showwarning("Invalid Input", "Depth must be a positive integer.")
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

            arr = sorted(self.generate_random_tree_array(min_value, max_value, depth))
            tree_root = self.build_random_tree(arr.copy(), 1, depth)

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

    def generate_random_tree_array(self, min_value, max_value, depth):
        max_nodes = 2**depth - 1
        all_values = list(range(min_value, max_value + 1))

        if max_nodes > len(all_values):
            # Không đủ giá trị duy nhất => cho phép trùng
            array = [random.choice(all_values) for _ in range(max_nodes)]
            if min_value not in array:
                array[0] = min_value
            if max_value not in array:
                array[-1] = max_value
            return array
        else:
            # Đủ giá trị => đảm bảo min và max có mặt
            base_values = all_values.copy()
            base_values.remove(min_value)
            if max_value != min_value:  # tránh remove 2 lần nếu bằng nhau
                base_values.remove(max_value)

            sample = random.sample(base_values, max_nodes - 2)
            sample += [min_value, max_value]
            random.shuffle(sample)
            return sample
        
    def build_random_tree(self, values, current_depth, max_depth):
        if not values or current_depth > max_depth:
            return None

        val = values.pop(random.randrange(len(values)))
        node = TreeNode(val)

        force_create = current_depth < 2  # Ép phải có nhánh lúc đầu cho chắc kèo

        # Random nhánh trái
        if values and (force_create or random.random() < 0.7):
            node.left = self.build_random_tree(values, current_depth + 1, max_depth)

        # Random nhánh phải
        if values and (force_create or random.random() < 0.7):
            node.right = self.build_random_tree(values, current_depth + 1, max_depth)

        return node

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
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Find Node")
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

        # Label căn trái
        tk.Label(popup, text="Enter value to find:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Frame chứa nút căn phải
        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(button_frame).pack(side="left", expand=True)  # Spacer đẩy nút sang phải

        def find_and_highlight():
            try:
                value = int(value_entry.get())
                node = self.find_node_by_value(self.root, value)
                if node:
                    self.highlighted_node = node
                    self.draw_tree(self.root)
                    self.scroll_to_node(node)
                    popup.destroy()
                else:
                    messagebox.showinfo("Not found", f"Node with value {value} not found.")
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
        cancel_button = tk.Button(button_frame, text="Cancel", command=popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        find_button = tk.Button(button_frame, text="Find", command=find_and_highlight, font=("Arial", 12))
        find_button.pack(side="right", padx=(5, 0))


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
            messagebox.showwarning("No Tree", "There is no tree to save.")
            return
        file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            arr = self.tree_to_array(self.root)
            # Ghi mảng ra file, mỗi giá trị cách nhau bởi dấu cách
            with open(file_path, "w") as f:
                f.write(" ".join(map(str, arr)))
            messagebox.showinfo("Save", "Tree saved successfully!")

    def load_tree_from_file(self):
        file_path = askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        with open(file_path, "r") as f:
            content = f.read().strip()
            if not content:
                messagebox.showwarning("Empty File", "The selected file is empty.")
                return
            arr = [int(x) for x in content.split()]
        loaded_tree = self.array_to_tree(arr)
        self.root = loaded_tree  # hoặc self.tree_root = loaded_tree
        self.draw_tree(self.root)
        if self.sidebar:
            arr = self.tree_to_array(self.root)
            self.sidebar.array = arr
            self.sidebar.update_array_display(arr)

    def create_random_tree(self, min_val, max_val, depth):
        
        max_nodes = 2**depth - 1
        all_values = list(range(min_val, max_val + 1))
        if max_nodes > len(all_values):
            values = [random.choice(all_values) for _ in range(max_nodes)]
            values[0] = min_val
            values[-1] = max_val
        else:
            base_values = all_values.copy()
            base_values.remove(min_val)
            if max_val != min_val:
                base_values.remove(max_val)
            values = random.sample(base_values, max_nodes - 2)
            values += [min_val, max_val]
            random.shuffle(values)

        def insert_random(root, val):
            if not root:
                return TreeNode(val)
            node = root
            while True:
                if random.choice([True, False]):
                    if node.left is None:
                        node.left = TreeNode(val)
                        break
                    else:
                        node = node.left
                else:
                    if node.right is None:
                        node.right = TreeNode(val)
                        break
                    else:
                        node = node.right
            return root

        root = None
        for v in values:
            root = insert_random(root, v)
        return root

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
        if self.zoom > 0.5:  # hoặc 0.7
            self.zoom /= 1.1
            self.draw_tree(self.root)
