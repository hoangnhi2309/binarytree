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
    def is_leaf(self):
        return self.left is None and self.right is None
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
    def clear_canvas(self):
        self.canvas.delete("all")
        self.node_positions.clear()
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
        pass  # Dự phòng xử lý click chuột phải

    def on_canvas_middle_click(self, event):
        pass  # Dự phòng xử lý click chuột giữa

    def show_node_menu(self, event, node):
# Hiển thị menu popup khi click vào node
        self.highlighted_node = node
        self.draw_tree(self.root)  # Vẽ lại cây để làm nổi bật node đang chọn

        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node(node))
        menu.add_command(label="Delete Node", command=lambda: self.delete_node(node))

# Tạo menu con cho "Add Node"
        add_menu = tk.Menu(menu, tearoff=0)
        add_menu.add_command(label="Left side", command=lambda: self.add_child_node(node, "left"))
        add_menu.add_command(label="Right side", command=lambda: self.add_child_node(node, "right"))
        menu.add_cascade(label="Add Node", menu=add_menu)

        menu.add_command(label="Switch Node", command=lambda: self.switch_node(node))
        menu.post(event.x_root, event.y_root)  # Hiển thị tại vị trí chuột

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
        center_x = root_x + (root_width // 2) - 150
        center_y = root_y + (root_height // 2) - 75
        popup.geometry(f"300x150+{center_x}+{center_y}")

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
        center_x = root_x + (root_width // 2) - 150
        center_y = root_y + (root_height // 2) - 100
        popup.geometry(f"300x200+{center_x}+{center_y}")

        tk.Label(popup, text="Enter value of the node to switch with:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)
        tk.Button(popup, text="Switch", command=lambda: self.perform_switch(node, value_entry), font=("Arial", 12)).pack(pady=10)

    def perform_switch(self, node, value_entry):
# Thực hiện hoán đổi giá trị giữa 2 node
        try:
            target_value = int(value_entry.get())
            target_node = self.find_node_by_value(self.root, target_value)
            if target_node is None:
                messagebox.showwarning("Node Not Found", f"Node with value {target_value} not found.")
                return
            node.val, target_node.val = target_node.val, node.val
            self.draw_tree(self.root)
            if self.sidebar:
                new_array = self.tree_to_array(self.root)
                self.sidebar.array = new_array
                self.sidebar.update_array_display(new_array)
            value_entry.master.destroy()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

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

    def draw_tree(self, root):
# Vẽ lại toàn bộ cây
        self.canvas.delete("all")
        if root:
            self._draw_subtree(root, 500, 40, 250)

    def _draw_subtree(self, node, x, y, x_offset):
        if node is None or node.val == 0:
            return

        # Chỉ vẽ nhánh và node nếu node con có giá trị khác 0
        if node.left and node.left.val != 0:
            self.canvas.create_line(x, y, x - x_offset, y + self.level_height)
            self._draw_subtree(node.left, x - x_offset, y + self.level_height, x_offset // 2)

        if node.right and node.right.val != 0:
            self.canvas.create_line(x, y, x + x_offset, y + self.level_height)
            self._draw_subtree(node.right, x + x_offset, y + self.level_height, x_offset // 2)

        color = "grey" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", 12, "bold"))
        self.nodes_positions.append((x, y, node))


    def tree_to_array(self, root):
        # Chuyển cây sang mảng bằng duyệt BFS, bỏ qua các node có giá trị 0
        result = []
        queue = [root]
        while queue:
            current = queue.pop(0)
            if current:
                left_val = current.left.val if current.left else 0
                right_val = current.right.val if current.right else 0
                # Nếu giá trị của node là 0, thì không đưa nó vào mảng
                if current.val != 0:
                    result.extend([current.val, left_val, right_val])
                queue.append(current.left)
                queue.append(current.right)
        return result
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
    
    # Thêm nút "Edit Array" vào Sidebar hoặc một vị trí phù hợp
        edit_array_button = tk.Button(self.sidebar, text="Edit Array", command=self.sidebar.edit_array)
        edit_array_button.pack(pady=10)

    def edit_array(self):
        if not self.array:
            messagebox.showwarning("No Array", "The array is empty. Please generate a tree first.")
            return

        # Tạo popup chỉnh sửa mảng
        popup = tk.Toplevel(self)
        popup.title("Edit Array")
        popup.geometry("400x300")
        popup.transient(self.winfo_toplevel())

        tk.Label(popup, text="Edit Array Values:", font=("Arial", 12)).pack(pady=10)

    # Hiển thị các ô nhập cho từng giá trị trong mảng
        entries = []
        for i, value in enumerate(self.array):
            frame = tk.Frame(popup)
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=f"Index {i}:", font=("Arial", 10)).pack(side="left", padx=5)
        entry = tk.Entry(frame, font=("Arial", 10))
        entry.insert(0, str(value))
        entry.pack(side="left", padx=5)
        entries.append(entry)

    # Nút lưu thay đổi
        tk.Button(popup, text="Save", command=lambda: self.save_array(entries, popup)).pack(pady=10)

def save_array(self, entries, popup):
    try:
        # Lấy giá trị mới từ các ô nhập
        new_array = [int(entry.get()) for entry in entries]

        # Cập nhật mảng và cây
        self.array = new_array
        self.tree_root = self.build_tree_from_list(new_array)
        if self.visualizer:
            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)

        # Đóng popup
        popup.destroy()
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter valid integers for all array values.")




    
  

