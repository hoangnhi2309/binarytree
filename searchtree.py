import tkinter as tk
import ttkbootstrap as ttk
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import random

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
        self.nodes_positions = []  # Lưu các vị trí của các node
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
        print(f"Click at: ({x_click}, {y_click})")  # In ra tọa độ click
        for x, y, node in self.nodes_positions:
            dx = x_click - x
            dy = y_click - y
            distance = (dx**2 + dy**2) ** 0.5
            print(f"Node position: ({x}, {y}), Distance: {distance}")  # In ra vị trí node và khoảng cách
            if distance <= self.node_radius:
                # Hiển thị cửa sổ chỉnh sửa node
                self.show_edit_node_window(node)
                break

    def add_random_child(self, node):
        new_value = random.randint(1, 100)  # Sinh giá trị ngẫu nhiên cho node mới
        new_node = TreeNode(new_value)
        direction = random.choice(["left", "right"])  # Chọn ngẫu nhiên con trái hoặc con phải
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

    def show_edit_node_window(self, node):
        # Tạo cửa sổ con
        edit_window = tk.Toplevel()
        edit_window.title("Edit Node")
        edit_window.geometry("300x200")  # Kích thước cửa sổ

        # Lấy kích thước màn hình
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()

        # Tính toán vị trí để đặt cửa sổ ở giữa màn hình
        window_width = 300
        window_height = 200
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Đặt vị trí cửa sổ
        edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        edit_window.transient(self.canvas.winfo_toplevel())  # Đặt cửa sổ con trên cửa sổ chính

        # Nhãn hiển thị giá trị hiện tại của node
        tk.Label(edit_window, text=f"Current Value: {node.val}", font=("Arial", 14)).pack(pady=10)

        # Entry để nhập giá trị mới
        tk.Label(edit_window, text="New Value:", font=("Arial", 12)).pack(pady=5)
        new_value_entry = tk.Entry(edit_window, font=("Arial", 12))
        new_value_entry.pack(pady=5)

        # Nút để lưu giá trị mới
        def save_new_value(new_value_entry):
            new_value = new_value_entry.get()
            if new_value.isdigit():
                node.val = int(new_value)  # Cập nhật giá trị node
                self.draw_tree(self.root)  # Vẽ lại cây
            if self.sidebar:
                new_array = self.tree_to_array(self.root)  # Cập nhật mảng từ cây
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)  # Hiển thị mảng mới
                edit_window.destroy()  # Đóng cửa sổ
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

        tk.Button(edit_window, text="Save", command=lambda: save_new_value(new_value_entry), font=("Arial", 12)).pack(pady=10)

        # Nút để xóa node
        def delete_node():
            # Lưu giá trị của node trước khi xóa
            nonlocal node
            deleted_value = node.val
            self.root = self._delete_node_recursive(self.root, node)  # Xóa node khỏi cây
            self.draw_tree(self.root)  # Vẽ lại cây
            if self.sidebar:
                # Cập nhật mảng từ cây
                new_array = self.tree_to_array(self.root)

                # Thay thế giá trị của node bị xóa bằng 0
                for i in range(len(self.sidebar.array)):
                    if self.sidebar.array[i] == deleted_value:
                        self.sidebar.array[i] = 0

                # Hiển thị mảng mới
                self.sidebar.update_array_display(self.sidebar.array)
            edit_window.destroy()  # Đóng cửa sổ

        tk.Button(edit_window, text="Delete Node", command=delete_node, font=("Arial", 12), fg="red").pack(pady=10)

    def delete_node(self, node, edit_window):
        self._delete_node_recursive(self.root, node)
        self.draw_tree(self.root)  # Vẽ lại cây
        if self.sidebar:
            new_array = self.tree_to_array(self.root)  # Cập nhật mảng từ cây
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)  # Hiển thị mảng mới
        edit_window.destroy()  # Đóng cửa sổ

    def _delete_node_recursive(self, current, target):
        if current is None:
            return None
        if current == target:
            return None
        current.left = self._delete_node_recursive(current.left, target)
        current.right = self._delete_node_recursive(current.right, target)
        return current

    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []  # Làm mới danh sách vị trí các node
        if root:
            self._draw_subtree(root, 500, 40, 250)

    def _draw_subtree(self, node, x, y, x_offset):
        # Vẽ nhánh trái
        if node.left:
            self.canvas.create_line(x, y, x - x_offset, y + self.level_height)
            self._draw_subtree(node.left, x - x_offset, y + self.level_height, x_offset // 2)
        # Vẽ nhánh phải
        if node.right:
            self.canvas.create_line(x, y, x + x_offset, y + self.level_height)
            self._draw_subtree(node.right, x + x_offset, y + self.level_height, x_offset // 2)

        # Màu sắc của node
        color = "grey" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", 12, "bold"))
        self.nodes_positions.append((x, y, node))  # Cập nhật vị trí node

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
        self.array = random.sample(range(1, 100), 7)
        self.tree_root = self.build_tree_from_list(self.array)
        if self.visualizer:
            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)
            new_array = self.visualizer.tree_to_array(self.tree_root)
            self.array = new_array
            self.update_array_display(new_array)

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


# ==== MAIN ====

if __name__ == "__main__":
    def show_page(name):
        print(f"Chuyển đến trang: {name}")
        header.set_active(name)

    root = tk.Tk()
    root.geometry("1200x700")
    root.title("TreeSim")

    header = Header(root, on_menu_click=show_page)
    sidebar = Sidebar(root)
    main_area = tk.Canvas(root, bg="lightgrey")
    main_area.pack(side="left", fill="both", expand=True)
    visualizer = BinaryTreeVisualizer(main_area)
    visualizer.bind_click_event()
    sidebar.visualizer = visualizer
    header.set_active("Binary Tree")
    visualizer.sidebar = sidebar
    root.mainloop()