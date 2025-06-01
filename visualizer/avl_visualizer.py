import tkinter as tk
import random
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer, TreeNode

class AVLVisualizer(BinaryTreeVisualizer):
    def height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def update_height(self, node):
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def right_rotate(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self.update_height(y)
        self.update_height(x)
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self.update_height(x)
        self.update_height(y)
        return y

    def insert_avl(self, root, key):
        if not root:
            return TreeNode(key)
        if key < root.val:
            root.left = self.insert_avl(root.left, key)
        elif key > root.val:
            root.right = self.insert_avl(root.right, key)
        else:
            return root  # Không chèn trùng

        self.update_height(root)
        balance = self.get_balance(root)

        # Xử lý 4 case mất cân bằng
        if balance > 1 and key < root.left.val:  # LL
            return self.right_rotate(root)
        if balance < -1 and key > root.right.val:  # RR
            return self.left_rotate(root)
        if balance > 1 and key > root.left.val:  # LR
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.val:  # RL
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def delete_avl(self, root, key):
        # 1. Nếu cây rỗng thì trả về None
        if not root:
            return root

        # 2. Tìm node cần xóa theo giá trị key
        if key < root.val:
            root.left = self.delete_avl(root.left, key)
        elif key > root.val:
            root.right = self.delete_avl(root.right, key)
        else:
            # Node cần xóa tìm thấy
            # Trường hợp node có 1 hoặc 0 con
            if not root.left:
                temp = root.right
                root = None
                return temp
            elif not root.right:
                temp = root.left
                root = None
                return temp
            
            # Trường hợp node có 2 con
            # Tìm node nhỏ nhất cây con bên phải (successor)
            temp = self.get_min_value_node(root.right)
            # Thay giá trị của node hiện tại bằng giá trị successor
            root.val = temp.val
            # Xóa node successor trong cây con bên phải
            root.right = self.delete_avl(root.right, temp.val)

        # Nếu cây con sau khi xóa trở nên rỗng thì trả về None
        if not root:
            return root

        # 3. Cập nhật chiều cao
        self.update_height(root)

        # 4. Kiểm tra cân bằng
        balance = self.get_balance(root)

        # 5. Xử lý 4 trường hợp mất cân bằng

        # Left Left Case
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)

        # Left Right Case
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        # Right Right Case
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)

        # Right Left Case
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root


    def get_min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None

        # Luôn lấy min và max, các giá trị còn lại lấy random
        if num_nodes == 1:
            values = [min_val]
        elif num_nodes == 2:
            values = [min_val, max_val]
        else:
            middle = list(range(min_val + 1, max_val))
            middle_nodes = random.sample(middle, num_nodes - 2)
            values = [min_val] + middle_nodes + [max_val]
            random.shuffle(values)

        root = None
        for val in values:
            root = self.insert_avl(root, val)
        return root

    def on_random_tree(self):
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.on_random_tree()
        else:
            tk.messagebox.showerror("Error", "Sidebar not found!")
    def get_array_representation(self):
        from collections import deque
        if not self.root:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

    def print_avl(self, node):
        if not node:
            return
        print(f"Node {node.val}: height={getattr(node, 'height', None)}, balance={self.get_balance(node)}")
        self.print_avl(node.left)
        self.print_avl(node.right)

    def show_node_menu(self, event, node):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node_popup(node))
        menu.add_command(label="Insert Node", command=self.insert_node)
        menu.add_command(label="Delete Node", command=lambda: self.delete_node_popup(node))
        menu.add_command(label="Show balance factor", command=lambda: self.show_balance_factor(node))
        # ... các mục khác nếu cần ...
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def insert_node(self):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Insert Node")
        popup.geometry("320x150")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center the popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 75
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(
            popup,
            text="Enter value to insert:",
            font=("Arial", 13),
            anchor="w"
        )
        label.pack(fill="x", padx=20, pady=(18, 2))

        entry = tk.Entry(popup, font=("Arial", 13))
        entry.pack(fill="x", padx=20, pady=(0, 10))

        def apply():
            try:
                new_val = int(entry.get())
                if self.search(self.root, new_val):
                    tk.messagebox.showwarning("Warning", "Value already exists in the tree!")
                    return
                self.root = self.insert_avl(self.root, new_val)
                self.draw_tree(self.root)
                if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                    arr = self.get_array_representation()
                    self.sidebar.update_array_display(arr)
                popup.destroy()
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a valid integer.")

        # Frame cho nút để căn phải
        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill="x", padx=10, pady=(0, 15))
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 12),
            width=8,
            command=popup.destroy
        )
        cancel_btn.pack(side="right", padx=(0, 5))
        agree_btn = tk.Button(
            btn_frame,
            text="Insert",
            font=("Arial", 12),
            width=8,
            command=apply
        )
        agree_btn.pack(side="right")
    def search(self, node, key):
            if node is None:
                print(f"search({key}): not found (node is None)")
                return False
            print(f"search({key}): checking node {node.val}")
            if key == node.val:
                print(f"search({key}): found")
                return True
            elif key < node.val:
                return self.search(node.left, key)
            else:
                return self.search(node.right, key)
    def delete_node_popup(self, node):
        result = tk.messagebox.askyesno("Delete Node", f"Are you sure you want to delete node {node.val}?")
        if result:
            self.root = self.delete_avl(self.root, node.val)
            self.draw_tree(self.root)
        if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
            arr = self.get_array_representation()
            self.sidebar.update_array_display(arr)
    def edit_node_popup(self, node):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Edit Node")
        popup.geometry("320x150")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 75
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(popup, text=f"Edit node {node.val} to:", font=("Arial", 13), anchor="w")
        label.pack(fill="x", padx=20, pady=(18, 2))

        entry = tk.Entry(popup, font=("Arial", 13))
        entry.pack(fill="x", padx=20, pady=(0, 10))

        def apply_edit():
            try:
                new_val = int(entry.get())
                old_val = node.val
                if new_val == old_val:
                    tk.messagebox.showinfo("Info", "New value is the same as old value.")
                    popup.destroy()
                    return
                if self.search(self.root, new_val):
                    tk.messagebox.showwarning("Warning", "Value already exists in the tree!")
                    return
                # Xóa node cũ và chèn node mới
                self.root = self.delete_avl(self.root, old_val)
                self.root = self.insert_avl(self.root, new_val)
                self.draw_tree(self.root)
                if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                    arr = self.get_array_representation()
                    self.sidebar.update_array_display(arr)
                popup.destroy()
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a valid integer.")

        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill="x", padx=10, pady=(0, 15))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), width=8, command=popup.destroy)
        cancel_btn.pack(side="right", padx=(0, 5))
        agree_btn = tk.Button(btn_frame, text="Apply", font=("Arial", 12), width=8, command=apply_edit)
        agree_btn.pack(side="right")
    def show_node_menu(self, event, node):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node_popup(node))
        menu.add_command(label="Insert Node", command=self.insert_node)
        menu.add_command(label="Delete Node", command=lambda: self.delete_node_popup(node))
        menu.add_command(label="Show balance factor", command=lambda: self.show_balance_factor(node))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()



    def show_balance_factor(self, node):
        bf = self.get_balance(node)
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Balance Factor")
        popup.geometry("260x120")
        popup.resizable(False, False)
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()

        # Center the popup
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 130
        y = popup.winfo_screenheight() // 2 - 60
        popup.geometry(f"+{x}+{y}")

        label = tk.Label(
            popup,
            text=f"Node {node.val}\nBalance factor = {bf}",
            font=("Arial", 14),
            padx=20,
            pady=20
        )
        label.pack(expand=True)

        close_btn = tk.Button(
            popup,
            text="Agree",
            font=("Arial", 12),
            width=8,
            command=popup.destroy
        )
        close_btn.pack(pady=(0, 15), padx=15, anchor="e", side="right")

