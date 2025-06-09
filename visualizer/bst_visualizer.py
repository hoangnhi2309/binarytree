import tkinter as tk
import tkinter.messagebox
import random
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer, TreeNode

# --- BST Visualizer kế thừa BinaryTreeVisualizer ---
class BSTVisualizer(BinaryTreeVisualizer):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.horizontal_spacing = 30
        self.level_height = 50
    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None

        values = list(range(min_val, max_val + 1))
        # Luôn giữ lại min_val và max_val
        selected = {min_val, max_val}

        # Lấy ngẫu nhiên các giá trị còn lại (trừ min/max)
        remaining = list(set(values) - selected)
        sample_count = num_nodes - 2 if num_nodes >= 2 else 0
        selected.update(random.sample(remaining, sample_count))

        values = list(selected)
        random.shuffle(values)  # Trộn lại thứ tự để tạo cây đa dạng

        root = None
        for val in values:
            root = self.insert_bst(root, val)
        return root

    def draw_tree(self, root):
        super().draw_tree(root)  # Gọi hàm cha để vẽ như cũ
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
    def insert_bst(self, root, val):
        if not root:
            return TreeNode(val)
        if val < root.val:
            root.left = self.insert_bst(root.left, val)
        elif val > root.val:
            root.right = self.insert_bst(root.right, val)
        return root
    def insert_node_popup(self, parent_node):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Insert Node")
        popup.geometry("320x150")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 75
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(popup, text=f"Insert new node value:", font=("Arial", 13), anchor="w")
        label.pack(fill="x", padx=20, pady=(18, 2))

        entry = tk.Entry(popup, font=("Arial", 13))
        entry.pack(fill="x", padx=20, pady=(0, 10))
        entry.focus_set()
        entry.select_range(0, 'end')

        error_label = tk.Label(popup, text="", fg="red", font=("Arial", 11))
        error_label.pack(fill="x", padx=20, pady=(0, 5))

        def apply_insert():
            try:
                new_val = int(entry.get())
                if self.search(self.root, new_val):
                    error_label.config(text="Value already exists in the tree!")
                    return
                self.root = self.insert_bst(self.root, new_val)
                self.draw_tree(self.root)
                if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                    arr = self.get_array_representation()
                    self.sidebar.update_array_display(arr)
                popup.destroy()
            except ValueError:
                error_label.config(text="Please enter a valid integer.")

        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill="x", padx=10, pady=(0, 15))
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), width=10, command=popup.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))
        agree_btn = tk.Button(btn_frame, text="Insert", font=("Arial", 12, "bold"), width=10, command=apply_insert)
        agree_btn.pack(side="right", padx=(0, 8))

        entry.bind("<Return>", lambda e: apply_insert())
        entry.bind("<Escape>", lambda e: popup.destroy())
    def show_node_menu(self, event, node):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node_popup(node))
        menu.add_command(label="Delete Node", command=lambda: self.delete_node_popup(node))
        menu.add_command(label="Insert Node", command=lambda: self.insert_node_popup(node))
        menu.add_command(label="Set as New Root", command=lambda: self.set_new_root(node))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    def edit_node_popup(self, node):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Edit Node")
        popup.geometry("320x170")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 85
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(popup, text=f"Edit node {node.val} to:", font=("Arial", 13), anchor="w")
        label.pack(fill="x", padx=20, pady=(18, 2))

        entry = tk.Entry(popup, font=("Arial", 13))
        entry.pack(fill="x", padx=20, pady=(0, 10))
        entry.focus_set()
        entry.bind("<Return>", lambda e: apply_edit())
        entry.bind("<Escape>", lambda e: popup.destroy())
        entry.bind("<FocusOut>", lambda e: popup.destroy() if not entry.get() else None)


        error_label = tk.Label(popup, text="", fg="red", font=("Arial", 11))
        error_label.pack(fill="x", padx=20, pady=(0, 5))

        def apply_edit():
            try:
                new_val = int(entry.get())
                if new_val == node.val:
                    popup.destroy()
                    return
                if self.search(self.root, new_val):
                    error_label.config(text="Value already exists in the tree!")
                    return
                self.root = self.delete_node(self.root, node.val)
                self.root = self.insert_bst(self.root, new_val)
                self.draw_tree(self.root)
                if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                    arr = self.get_array_representation()
                    self.sidebar.update_array_display(arr)
                popup.destroy()
            except ValueError:
                error_label.config(text="Please enter a valid integer.")

        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill="x", padx=10, pady=(0, 15))
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), width=10, command=popup.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))
        agree_btn = tk.Button(btn_frame, text="Apply", font=("Arial", 12, "bold"), width=10, command=apply_edit)
        agree_btn.pack(side="right", padx=(0, 8))
        
    def search(self, root, key):
        if not root:
            return False
        if key == root.val:
            return True
        elif key < root.val:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)
    def delete_node(self, root, key):
        if not root:
            return None
        if key < root.val:
            root.left = self.delete_node(root.left, key)
        elif key > root.val:
            root.right = self.delete_node(root.right, key)
        else:
            # Node cần xóa tìm thấy
            if not root.left:
                return root.right
            elif not root.right:
                return root.left
            # Node có 2 con: tìm node nhỏ nhất bên phải
            temp = root.right
            while temp.left:
                temp = temp.left
            root.val = temp.val
            root.right = self.delete_node(root.right, temp.val)
        return root
    def delete_node_popup(self, node):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Delete Node")
        popup.geometry("320x130")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 65
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(popup, text=f"Delete node {node.val}?", font=("Arial", 13, "bold"), anchor="center")
        label.pack(fill="x", padx=20, pady=(20, 10))

        def do_delete():
            self.root = self.delete_node(self.root, node.val)
            self.draw_tree(self.root)
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                arr = self.get_array_representation()
                self.sidebar.update_array_display(arr)
            popup.destroy()


        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill="x", padx=10, pady=(0, 15))
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), width=10, command=popup.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))
        delete_btn = tk.Button(btn_frame, text="Delete", font=("Arial", 12), width=10, command=do_delete)
        delete_btn.pack(side="right", padx=(0, 8))

    def on_random_tree(self):
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.on_random_tree()
        else:
            tk.messagebox.showerror("Error", "Sidebar not found!")

    def get_array_representation(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if not node:
            return
        self._inorder(node.left, result)
        result.append(node.val)
        self._inorder(node.right, result)
        
    def rebuild_with_new_root(self, new_root_node):
        # Duyệt cây hiện tại để lấy toàn bộ giá trị
        all_values = self.inorder_traversal(self.root)

        # Đảm bảo không bị lỗi nếu node bị trùng
        all_values.remove(new_root_node.val)
        random.shuffle(all_values)

        # Tạo cây mới với node được chọn làm root
        self.root = TreeNode(new_root_node.val)
        for val in all_values:
            self.root = self.insert_bst(self.root, val)

        self.draw_tree(self.root)

        if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
            arr = self.get_array_representation()
            self.sidebar.update_array_display(arr)
    
    def set_new_root(self, node):
        self.rebuild_with_new_root(node)
    def inorder_traversal(self, root):
        if not root:
            return []
        return self.inorder_traversal(root.left) + [root.val] + self.inorder_traversal(root.right)
    def _calculate_positions(self, node, depth=0, x_offset=0, total_nodes=None):
        if total_nodes is None:
            # Đếm tổng số node để căn giữa
            total_nodes = self.count_nodes(self.root)
            self._x_start = (self.canvas.winfo_width() // 2) - ((total_nodes // 2) * self.horizontal_spacing)
        if not node:
            return x_offset

        x_offset = self._calculate_positions(node.left, depth + 1, x_offset, total_nodes)

        # Đặt vị trí node hiện tại dựa trên thứ tự inorder, căn giữa canvas
        node.x = self._x_start + x_offset * self.horizontal_spacing
        node.y = depth * self.level_height + 60
        self.nodes_positions.append((node, node.x, node.y))

        x_offset += 1
        x_offset = self._calculate_positions(node.right, depth + 1, x_offset, total_nodes)

        return x_offset

    def count_nodes(self, node):
        if not node:
            return 0
        return 1 + self.count_nodes(node.left) + self.count_nodes(node.right)