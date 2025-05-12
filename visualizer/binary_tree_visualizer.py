import tkinter as tk
import tkinter.ttk as ttk
import random
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk



# ==== Cây nhị phân đơn giản ====

class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None
class BinaryTreeVisualizer:
    def __init__(self, canvas):
        self.tree_root = None
        self.controller = None
        self.canvas = canvas
        # Bán kính node hình tròn
        self.node_radius = 20 
        # Khoảng cách theo chiều dọc giữa các mức
        self.level_height = 80
        # Node đang được chọn
        self.highlighted_node = None  
        # Lưu vị trí các node để xử lý click chuột
        self.nodes_positions = [] 
        # Gốc của cây
        self.root = None
        # Sidebar để cập nhật mảng đại diện cây
        self.sidebar = None
        
    def set_controller(self, controller):
        self.controller = controller
#Thiết lập (cập nhật) node gốc (root) của cây nhị phân.
#Trả về node gốc hiện tại của cây nhị phân để phục vụ thao tác khác.
    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def bind_click_event(self):
        # Gắn sự kiện chuột trái, phải, giữa cho canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)       # Click trái: mở menu node
        self.canvas.bind("<Button-3>", self.on_canvas_right_click) # Click phải: dự phòng
        self.canvas.bind("<Button-2>", self.on_canvas_middle_click)# Click giữa: dự phòng

    def on_canvas_click(self, event):
        # Kiểm tra xem có click vào node nào không, nếu có thì hiện menu
        x, y = event.x, event.y
        for pos in self.nodes_positions:
            node_x, node_y, node = pos
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                break

    def on_canvas_right_click(self, event):
        pass  

    def on_canvas_middle_click(self, event):
        pass  

    def show_node_menu(self, event, node):
        # Đổi màu node được click
        self.highlighted_node = node
        self.draw_tree(self.root)  # Vẽ lại cây để cập nhật màu sắc

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
        # Duyệt cây theo BFS để chuyển đổi thành mảng
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
                result.append(0)  # Node rỗng được biểu diễn bằng 0
        return result
    
    
    def edit_node(self, node):
# Hiển thị popup chỉnh sửa giá trị của node
        popup = tk.Toplevel(self.canvas)
        popup.title("Edit Node")
        popup.geometry("300x150")
        popup.transient(self.canvas.winfo_toplevel())
# Căn giữa popup
        root_x = self.canvas.winfo_toplevel().winfo_rootx()
        root_y = self.canvas.winfo_toplevel().winfo_rooty()
        root_width = self.canvas.winfo_toplevel().winfo_width()
        root_height = self.canvas.winfo_toplevel().winfo_height()

        popup_width = 300
        popup_height = 150
        center_x = root_x + (root_width // 2) - (popup_width // 2)
        center_y = root_y + (root_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        
# Giao diện nhập giá trị mới
        tk.Label(popup, text="New Value:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)
        tk.Button(popup, text="Save", command=lambda: self.save_value(node, value_entry, popup), font=("Arial", 12)).pack(pady=10)

    def save_value(self, node, value_entry, popup):
# Lưu giá trị mới vào node
        try:
            new_value = int(value_entry.get())
            node.val = new_value
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                print(f"New Array: {new_array}")  # Kiểm tra mảng sau khi thay đổi
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)
            popup.destroy()
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
            self.root = None
        else:
            find_and_remove(None, self.root, node)

        self.draw_tree(self.root)
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            new_array = [0 if val is None else val for val in new_array]
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def add_child_node(self, node, direction):
 # Thêm node con trái/phải nếu chưa tồn tại
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

        self.draw_tree(self.root)
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)
            return

    def switch_node(self, node):
 # Hiển thị popup để nhập giá trị node cần hoán đổi
        popup = tk.Toplevel(self.canvas)
        popup.title("Switch Node")
        popup.geometry("300x200")
        popup.transient(self.canvas.winfo_toplevel())

# Căn giữa popup
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

    def perform_switch(self, node, value_entry, popup):
        try:
            target_value = int(value_entry.get())
            target_node = self.find_node_by_value(self.root, target_value)
            if target_node is None:
                messagebox.showwarning("Node Not Found", f"Node with value {target_value} not found.")
                return

            node.val, target_node.val = target_node.val, node.val  # Hoán đổi giá trị
            self.draw_tree(self.root)  # Vẽ lại cây
            if self.sidebar:
                new_array = self.tree_to_array(self.root)  # Cập nhật mảng
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)
            popup.destroy()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

    def find_node_by_value(self, root, value):
# Tìm node theo giá trị
        if root is None:
            return None
        if root.val == value:
            return root
        left_result = self.find_node_by_value(root.left, value)
        if left_result:
            return left_result
        return self.find_node_by_value(root.right, value)

    def _draw_node(self, node, x, y, dx, level):
        if node is None:
            return

        self._draw_circle(x, y, str(node.val))

        if node.left is not None:
            self._draw_line(x, y, x - dx, y + self.level_height)
            self._draw_node(node.left, x - dx, y + self.level_height, dx / 2, level + 1)
        if node.right is not None:
            self._draw_line(x, y, x + dx, y + self.level_height)
            self._draw_node(node.right, x + dx, y + self.level_height, dx / 2, level + 1)
    