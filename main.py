import tkinter as tk
import tkinter.ttk as ttk
import random
import threading
import time
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import os
# ==== Cây nhị phân đơn giản ====

class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None

class BinaryTreeVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_radius = 20
        self.level_height = 80
        self.highlighted_node = None
        self.nodes_positions = []
        self.root = None
        self.sidebar = None

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def bind_click_event(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        x_click, y_click = event.x, event.y
        for x, y, node in self.nodes_positions:
            dx = x_click - x
            dy = y_click - y
            distance = (dx**2 + dy**2) ** 0.5
            if distance <= self.node_radius:
                # Hiển thị menu khi nhấn vào node
                self.show_node_menu(event, node)
                return

    
    def show_node_menu(self, event, node):
    # Tạo menu popup
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node(node))
        menu.add_command(label="Delete Node", command=lambda: self.delete_node(node))
        # Tạo menu con cho "Add Node"
        add_menu = tk.Menu(menu, tearoff=0)
        add_menu.add_command(label="Left side", command=lambda: self.add_child_node(node, "left"))
        add_menu.add_command(label="Right side", command=lambda: self.add_child_node(node, "right"))
        menu.add_cascade(label="Add Node", menu=add_menu)
        menu.add_command(label="Switch Node", command=lambda: self.switch_node(node))
        menu.post(event.x_root, event.y_root)  # Hiển thị menu tại vị trí nhấn chuột

    def edit_node(self, node):
    # Hiển thị popup để chỉnh sửa giá trị của node
        popup = tk.Toplevel(self.canvas)
        popup.title("Edit Node")
        popup.geometry("300x150")
        popup.transient(self.canvas.winfo_toplevel())  # Hiển thị popup ở giữa cửa sổ chính

    # Tính toán vị trí trung tâm
        root_x = self.canvas.winfo_toplevel().winfo_rootx()
        root_y = self.canvas.winfo_toplevel().winfo_rooty()
        root_width = self.canvas.winfo_toplevel().winfo_width()
        root_height = self.canvas.winfo_toplevel().winfo_height()

        popup_width = 300
        popup_height = 150
        center_x = root_x + (root_width // 2) - (popup_width // 2)
        center_y = root_y + (root_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")

        tk.Label(popup, text="New Value:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)
        tk.Button(popup, text="Save",command=lambda: self.save_value(node, value_entry, popup), font=("Arial", 12)).pack(pady=10)

    def save_value(self, node, value_entry, popup):
        try:
            new_value = int(value_entry.get())  # Lấy giá trị mới từ ô nhập
            node.val = new_value  # Cập nhật giá trị của node
            self.draw_tree(self.root)  # Vẽ lại cây
            # Cập nhật mảng trong sidebar
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)
                popup.destroy()  # Đóng popup sau khi lưu
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
    
    def delete_node(self, node):
    # Xóa node khỏi cây
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
            self.root = None  # Xóa root nếu node là root
        else:
            find_and_remove(None, self.root, node)

        self.draw_tree(self.root)  # Vẽ lại cây để cập nhật giao diện
        # Cập nhật mảng trong sidebar
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
        # Thay thế các giá trị None bằng 0
            new_array = [0 if val is None else val for val in new_array]
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def add_child_node(self, node, direction):
    # Tạo node mới với giá trị ngẫu nhiên
        new_value = random.randint(1, 100)
        new_node = TreeNode(new_value)

        if direction == "left":
            if node.left is None:
                node.left = new_node
            else:
                messagebox.showwarning("Node Exists", "Node bên trái đã tồn tại.")
                return
        elif direction == "right":
            if node.right is None:
                node.right = new_node
            else:
                messagebox.showwarning("Node Exists", "Node bên phải đã tồn tại.")
                return
        # Vẽ lại cây và cập nhật sidebar
        self.draw_tree(self.root)
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)
            return

    def tree_to_array(self, root):
            result = []
            queue = [root]
            while queue:
                current = queue.pop(0)
                if current:
                    result.append(current.val)
                    queue.append(current.left)
                    queue.append(current.right)
                else:
                    result.append(0)  # Thêm giá trị 0 nếu node không tồn tại
            print(f"Updated array: {result}")  # Thêm thông báo kiểm tra
            return result

    def switch_node(self, node):
    # Hiển thị popup để chọn giá trị của node cần hoán đổi
        popup = tk.Toplevel(self.canvas)
        popup.title("Switch Node")
        popup.geometry("300x200")
        popup.transient(self.canvas.winfo_toplevel())  # Hiển thị popup ở giữa cửa sổ chính

    # Tính toán vị trí trung tâm
        root_x = self.canvas.winfo_toplevel().winfo_rootx()
        root_y = self.canvas.winfo_toplevel().winfo_rooty()
        root_width = self.canvas.winfo_toplevel().winfo_width()
        root_height = self.canvas.winfo_toplevel().winfo_height()

        popup_width = 300
        popup_height = 200
        center_x = root_x + (root_width // 2) - (popup_width // 2)
        center_y = root_y + (root_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        tk.Label(popup, text="Enter value of the node to switch with:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)

        tk.Button(popup, text="Switch", command=lambda: self.perform_switch(node, value_entry), font=("Arial", 12)).pack(pady=10)

    def perform_switch(self, node, value_entry):
        try:
            target_value = int(value_entry.get())  # Lấy giá trị của node cần hoán đổi
            target_node = self.find_node_by_value(self.root, target_value)
            if target_node is None:
                messagebox.showwarning("Node Not Found", f"Node with value {target_value} not found.")
                return

            # Hoán đổi giá trị giữa hai node
            node.val, target_node.val = target_node.val, node.val

            # Vẽ lại cây và cập nhật sidebar
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                print(f"Updated array after switch: {new_array}")  # Thêm thông báo kiểm tra
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)  # Cập nhật bảng array trong sidebar
                value_entry.master.destroy()  # Đóng popup sau khi hoán đổi
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def find_node_by_value(self, root, value):
        if root is None:
            return None
        if root.val == value:
            return root
        left_result = self.find_node_by_value(root.left, value)
        if left_result:
            return left_result
        return self.find_node_by_value(root.right, value)

    # Vẽ lại cây và cập nhật sidebar
    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []
        if root:
            self._draw_subtree(root, 500, 40, 250)

    def add_random_child(self, node):
        new_value = random.randint(1, 100)
        new_node = TreeNode(new_value)
        direction = random.choice(["left", "right"])
        if direction == "left":
            if node.left is None:
                node.left = new_node
            elif node.right is None:
                node.right = new_node
        else:
            if node.right is None:
                node.right = new_node
            elif node.left is None:
                node.left = new_node
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def tree_to_array(self, root):
        result = []
        queue = [root]
        while queue:
            current = queue.pop(0)
        if current:
            result.append(current.val)
            queue.append(current.left)
            queue.append(current.right)
        else:
            result.append(0)  # Thêm giá trị 0 nếu node không tồn tại
        return result

    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []
        if root:
            self._draw_subtree(root, 500, 40, 250)

    def _draw_subtree(self, node, x, y, x_offset):
        if node.left:
            self.canvas.create_line(x, y, x - x_offset, y + self.level_height)
            self._draw_subtree(node.left, x - x_offset, y + self.level_height, x_offset // 2)
        if node.right:
            self.canvas.create_line(x, y, x + x_offset, y + self.level_height)
            self._draw_subtree(node.right, x + x_offset, y + self.level_height, x_offset // 2)

        color = "grey" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", 12, "bold"))
        self.nodes_positions.append((x, y, node))

    def tree_to_array(self, root):
        result = []
        queue = [root]
        while queue:
            current = queue.pop(0)
            if current:
                left_val = current.left.val if current.left else 0
                right_val = current.right.val if current.right else 0
                result.extend([current.val, left_val, right_val])
                queue.append(current.left)
                queue.append(current.right)
        return result


# ==== HEADER ====

class Header(tk.Frame):
    def __init__(self, parent, on_menu_click):
        super().__init__(parent, bg="#b0b0b0")
        self.pack(fill='x')

        self.on_menu_click = on_menu_click
        self.menu_buttons = {}

        logo_image = Image.open("binarytree.png").resize((75, 75))
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self, image=self.logo_photo, bg="#b0b0b0")
        logo_label.pack(side="left", padx=(10, 5), pady=5)

        menu_items = ["Binary Tree", "Binary Search Tree", "AVL Tree"]
        for item in menu_items:
            normal_font = ("Arial", 20, "bold")
            underline_font = ("Arial", 20, "bold", "underline")

            btn = tk.Label(self, text=item, font=normal_font,
                           bg="#b0b0b0", fg="black", cursor="hand2")
            btn.pack(side="left", padx=30)
            btn.bind("<Enter>", lambda e, b=btn: b.config(font=underline_font))
            btn.bind("<Leave>", lambda e, b=btn: b.config(font=normal_font))
            btn.bind("<Button-1>", lambda e, name=item: self.menu_clicked(name))

            self.menu_buttons[item] = btn

    def menu_clicked(self, name):
        self.set_active(name)
        self.on_menu_click(name)

    def set_active(self, active_name):
        for name, btn in self.menu_buttons.items():
            if name == active_name:
                btn.config(fg="#164933", font=("Arial", 20, "bold", "underline"))
            else:
                btn.config(fg="black", font=("Arial", 20, "bold"))


# ==== SIDEBAR ====

class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="grey", width=400)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)
        self.tree_root = None
        self.array = []
        self.visualizer = None
        self.highlighted_node = None

        array_label = tk.Label(self, text="Array:", font=("Arial", 20, "bold"), bg="grey", fg="black")
        array_label.pack(anchor="w", padx=20, pady=(0, 5))

        array_frame = tk.Frame(self, bg="grey")
        array_frame.pack(padx=20, pady=10, fill="both", expand=False)

        self.array_display = tk.Text(
            array_frame,
            wrap="none",
            height=12,
            font=("Arial", 14),
            bg="white",
            relief="solid",
            bd=1,
            padx=10,
            pady=10,
            insertborderwidth=4
        )
        self.array_display.pack(side="left", fill="both", expand=True)

        scroll = tk.Scrollbar(array_frame, command=self.array_display.yview)
        scroll.pack(side="right", fill="y")
        self.array_display.config(yscrollcommand=scroll.set, state="disabled")

        search_title = tk.Label(self, text="Find:", font=("Arial", 18, "bold"), bg="grey", fg="black")
        search_title.pack(anchor="w", padx=20, pady=(10, 5))

        search_frame = tk.Frame(self, relief="flat", bg="grey", bd=5, highlightthickness=0)
        search_frame.pack(fill="x", padx=20)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(side="left", fill="x", expand=True)

        search_btn = tk.Button(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            relief="flat",
            bg="grey",
            command=self.on_search_node
        )
        search_btn.pack(side="left", padx=(5, 0))

        self.create_modern_button("Create random tree", self.on_random_tree)
        self.create_modern_button("Delete", self.on_clear_tree)
        self.create_modern_button("Save to file", self.save_tree_to_file)

    def format_array_multiline(self, array):
        lines = []
        for i in range(0, len(array), 3):
            group = array[i:i+3]
            line = ", ".join(str(val) for val in group)
            lines.append(line)
        return "\n".join(lines)

    def update_array_display(self, array):
        self.array_display.config(state="normal")
        self.array_display.delete("1.0", tk.END)
        self.array_display.insert("1.0", self.format_array_multiline(array))
        self.array_display.config(state="disabled")

    def save_tree_to_file(self):
        if not self.array:
            messagebox.showwarning("Empty Tree", "There is no tree to save.")
            return

        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Tree As"
        )

        if not file_path:
            return  # người dùng bấm Cancel

        content = self.format_array_multiline(self.array)
        try:
            with open(file_path, "w") as f:
                f.write(content)
            messagebox.showinfo("Success", f"Tree saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def on_search_node(self):
        value = self.search_entry.get()
        if value.isdigit():
            value = int(value)
            if value in self.array:
                self.highlighted_node = self._find_node(self.tree_root, value)
                if self.visualizer:
                    self.visualizer.highlighted_node = self.highlighted_node
                    self.visualizer.draw_tree(self.tree_root)
            else:
                messagebox.showinfo("Node Not Found", f"Node {value} not found in the array.")
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

    def _find_node(self, root, value):
        if root is None:
            return None
        if root.val == value:
            return root
        left_result = self._find_node(root.left, value)
        if left_result:
            return left_result
        return self._find_node(root.right, value)

    def on_random_tree(self):
    # Tạo popup để nhập min và max
        self.popup = tk.Toplevel(self)  # Lưu popup vào self.popup
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x200")
        self.popup.transient(self.winfo_toplevel())  # Hiển thị popup ở giữa cửa sổ chính

        tk.Label(self.popup, text="Min Value:", font=("Arial", 12)).pack(pady=5)
        self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.min_entry.pack(pady=5)

        tk.Label(self.popup, text="Max Value:", font=("Arial", 12)).pack(pady=5)
        self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.max_entry.pack(pady=5)

        tk.Button(self.popup, text="Create", command=self.create_tree, font=("Arial", 12)).pack(pady=10)

    def create_tree(self):
        try:
            min_value = int(self.min_entry.get())
            max_value = int(self.max_entry.get())
            if min_value >= max_value:
                messagebox.showwarning("Invalid Input", "Min value must be less than Max value.")
                return

            # Tạo cây ngẫu nhiên với giá trị trong khoảng [min_value, max_value]
            self.array = random.sample(range(min_value, max_value + 1), 7)
            self.tree_root = self.build_tree_from_list(self.array)
            if self.visualizer:
                    self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)
            new_array = self.visualizer.tree_to_array(self.tree_root)
            self.array = new_array
            self.update_array_display(new_array)


            self.popup.destroy()  # Đóng popup sau khi tạo cây
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid integers for Min and Max.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        

    def on_clear_tree(self):
        self.tree_root = None
        self.array = []
        self.highlighted_node = None
        self.update_array_display([])
        if self.visualizer:
            self.visualizer.canvas.delete("all")

    def build_tree_from_list(self, lst):
        if not lst:
            return None
        nodes = [TreeNode(val) for val in lst]
        for i in range(len(lst)):
            left_index = 2 * i + 1
            right_index = 2 * i + 2
            if left_index < len(lst):
                nodes[i].left = nodes[left_index]
            if right_index < len(lst):
                nodes[i].right = nodes[right_index]
        return nodes[0]

    def create_modern_button(self, text, command):
        btn = tk.Label(
            self,
            text=text,
            font=("Arial", 14),
            bg="#ffffff",
            fg="#333333",
            bd=2,
            cursor="hand2"
        )
        btn.pack(padx=20, fill="x", pady=(10, 5))
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="white"))
        btn.bind("<Button-1>", lambda e: command())

# ====== FINAL TraversalBar: Flat style, sidebar color ======
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





# ==== MAIN CHUẨN HÓA BỐ CỤC ====

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

    # Traversal bar gắn vào dưới cùng của vùng vẽ
    traversal_bar = TraversalBar(right_frame, visualizer, tree_getter=lambda: sidebar.tree_root)

    root.mainloop()

