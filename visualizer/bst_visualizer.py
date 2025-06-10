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
    def on_find_node(self):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Find Node")
        popup.geometry("320x130")
        popup.resizable(False, False)

        label = tk.Label(popup, text="Enter value to find:", font=("Arial", 12))
        label.pack(pady=(10, 0))

        entry = tk.Entry(popup, font=("Arial", 12))
        entry.pack(pady=(0, 10))

        def find_node():
            value = entry.get()
            # Implement the logic to find the node in the BST
            # If found, highlight the node
            # If not found, show an error message
            popup.destroy()

        find_button = tk.Button(popup, text="Find", command=find_node)
        find_button.pack(pady=(0, 10))

    def show_canvas_menu(self, event, node):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Find node", command=self.on_find_node)
        menu.add_command(label="Create random tree", command=self.on_random_tree)
    # ...
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


# --- Sidebar class chính ---
class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgrey", width=300)

        self.visualizer = None
        self.tree_root = None
        self.popup = None  # để tránh lỗi chưa khai báo

        self.create_random_tree_btn = tk.Button(
            self, text="Create random tree", command=lambda: self.visualizer.on_random_tree(),
            font=("Arial", 12), bg="grey", fg="white"
        )
        self.create_random_tree_btn.pack(pady=10, padx=10, fill="x")

    def on_random_tree(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.winfo_toplevel())

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

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, BSTVisualizer):
            label_text = "Tree Depth:"
        else:
            label_text = "Number of Nodes:"

        tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.extra_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.extra_entry.insert(0, "3")
        self.extra_entry.pack(fill="x", padx=10, pady=(0, 10))

        cancel_button = tk.Button(self.popup, text="Cancel", command=self.popup.destroy,
                                  font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5), pady=10)

        create_button = tk.Button(self.popup, text="Create", command=self.handle_create_tree,
                                  font=("Arial", 12), bg="grey", fg="white")
        create_button.pack(side="right", padx=(5, 0), pady=10)

    def handle_create_tree(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            extra = int(self.extra_entry.get())

            if min_val > max_val or extra <= 0:
                raise ValueError("Min > Max hoặc extra <= 0")

            self.tree_root = self.visualizer.create_random_tree(min_val, max_val, extra)

            if self.tree_root is None:
                raise ValueError("Không tạo được cây")

            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)

            if hasattr(self, "tree_to_array") and hasattr(self, "update_array_display"):
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)

            self.popup.destroy()

        except Exception as e:
            print("DEBUG ERROR:", e)
            tk.messagebox.showerror("Lỗi", "Thông số không hợp lệ hoặc không tạo được cây.")

    def on_array_value_change(self, new_value, index):
        if self.visualizer.selected_node:
            self.visualizer.selected_node.val = new_value
            self.visualizer.draw_tree(self.tree_root)
        else:
            tk.messagebox.showinfo("Info", "Hãy chọn một node trên cây trước khi sửa giá trị.")

    def update_array_display(self, array):
        # Lưu lại array hiện tại để dùng cho update
        self.array = array.copy()
        # Xóa frame cũ nếu có
        if hasattr(self, "array_frame"):
            self.array_frame.destroy()
        self.array_frame = tk.Frame(self)
        self.array_frame.pack(pady=10)

        self.array_entries = []
        for i, val in enumerate(array):
            entry = tk.Entry(self.array_frame, width=5, font=("Arial", 12))
            entry.insert(0, str(val))
            entry.grid(row=0, column=i, padx=2)
            self.array_entries.append(entry)

        # Thêm nút Update Tree
        update_btn = tk.Button(self.array_frame, text="Update Tree", font=("Arial", 12), bg="blue", fg="white",
                               command=self.on_update_tree)
        update_btn.grid(row=1, column=0, columnspan=len(array), pady=5)
            
    def on_update_tree(self):
        try:
            new_values = [int(entry.get()) for entry in self.array_entries]
            # Duyệt cây theo inorder để lấy danh sách node
            inorder_nodes = []
            def inorder(node):
                if not node:
                    return
                inorder(node.left)
                inorder_nodes.append(node)
                inorder(node.right)
            inorder(self.tree_root)

            if len(new_values) != len(inorder_nodes):
                tk.messagebox.showerror("Lỗi", "Số lượng giá trị không khớp số node trong cây.")
                return

            # Kiểm tra tính chất BST: dãy inorder phải tăng dần
            for i in range(1, len(new_values)):
                if new_values[i] <= new_values[i-1]:
                    tk.messagebox.showerror("Lỗi", "Giá trị mới không thỏa mãn tính chất BST (inorder phải tăng dần).")
                    return

            changed = False
            for i, (node, val) in enumerate(zip(inorder_nodes, new_values)):
                if val != self.array[i]:
                    node.val = val
                    changed = True

            if changed:
                self.visualizer.draw_tree(self.tree_root)
                if hasattr(self, "tree_to_array"):
                    self.array = self.tree_to_array(self.tree_root)
                    self.update_array_display(self.array)
                tk.messagebox.showinfo("Thành công", "Cập nhật giá trị node thành công.")
            else:
                tk.messagebox.showinfo("Thông báo", "Không có giá trị nào thay đổi.")

        except Exception as e:
            tk.messagebox.showerror("Lỗi", "Giá trị nhập không hợp lệ.")

    def tree_to_array(self, root):
        res = []
        def inorder(node):
            if not node:
                return
            inorder(node.left)
            res.append(node.val)
            inorder(node.right)
        inorder(root)
        return res

    def update_edit(self):
        text = self.array_display.get("1.0", "end").strip()
        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            # --- Xử lý cho Binary Tree ---
            lines = text.split("\n")
            new_vals = []
            for line in lines:
                parts = line.split(",")
                if len(parts) != 3:
                    self.show_toast_notification("Error: Each line must have exactly 3 values (val, left, right).")
                    return
                try:
                    val = int(parts[0].strip())
                    new_vals.append(val)
                except ValueError:
                    self.show_toast_notification("Error: All values must be integers.")
                    return

            queue = [self.tree_root] if self.tree_root else []
            idx = 0
            changed = False
            while queue and idx < len(new_vals):
                node = queue.pop(0)
                if node:
                    if node.val != new_vals[idx]:
                        node.val = new_vals[idx]
                        changed = True
                    idx += 1
                    queue.append(node.left)
                    queue.append(node.right)

            if changed:
                self.visualizer.draw_tree(self.tree_root)
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)
                self.show_toast_notification("Node values updated successfully.")
            else:
                self.show_toast_notification("No values changed.")

        else:
            # --- Xử lý cho BST/AVL ---
            parts = [p.strip() for p in text.split(",") if p.strip()]
            try:
                new_vals = [int(val) for val in parts]
            except ValueError:
                self.show_toast_notification("Error: All values must be integers.")
                return

            inorder_nodes = []
            def inorder(node):
                if not node:
                    return
                inorder(node.left)
                inorder_nodes.append(node)
                inorder(node.right)
            inorder(self.tree_root)

            if len(new_vals) != len(inorder_nodes):
                self.show_toast_notification("Error: Số lượng giá trị không khớp số node trong cây.")
                return

            changed = False
            for node, val in zip(inorder_nodes, new_vals):
                if node.val != val:
                    node.val = val
                    changed = True

            if changed:
                self.visualizer.draw_tree(self.tree_root)
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)
                self.show_toast_notification("Node values updated successfully.")
            else:
                self.show_toast_notification("No values changed.")

    def count_nodes(self, node):
        if not node:
            return 0
        return 1 + self.count_nodes(node.left) + self.count_nodes(node.right)
