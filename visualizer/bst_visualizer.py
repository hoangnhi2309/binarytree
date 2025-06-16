import tkinter as tk
import tkinter.messagebox
import random
from tkinter.filedialog import askopenfilename, asksaveasfilename
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer, TreeNode

class BSTVisualizer(BinaryTreeVisualizer):
    def __init__(self, canvas):
        super().__init__(canvas)

    def create_random_tree(self, min_val, max_val, num_nodes):
        if max_val - min_val + 1 < num_nodes:
            tk.messagebox.showerror("Error", "Không đủ số lượng giá trị duy nhất trong khoảng để tạo cây.")
            return None
        values = list(range(min_val, max_val + 1))
        selected = {min_val, max_val}
        remaining = list(set(values) - selected)
        sample_count = num_nodes - 2 if num_nodes >= 2 else 0
        selected.update(random.sample(remaining, sample_count))
        values = list(selected)
        random.shuffle(values)
        root = None
        for val in values:
            root = self.insert_bst(root, val)
        return root

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
        popup.update_idletasks()
        x = popup.winfo_screenwidth() // 2 - 160
        y = popup.winfo_screenheight() // 2 - 85
        popup.geometry(f"+{x}+{y}")
        label = tk.Label(popup, text=f"Edit node {node.val} to:", font=("Arial", 13), anchor="w")
        label.pack(fill="x", padx=20, pady=(18, 2))
        entry = tk.Entry(popup, font=("Arial", 13))
        entry.pack(fill="x", padx=20, pady=(0, 10))
        entry.focus_set()
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
        entry.bind("<Return>", lambda e: apply_edit())
        entry.bind("<Escape>", lambda e: popup.destroy())

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
            if not root.left:
                return root.right
            elif not root.right:
                return root.left
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

    def _inorder(self, node, result):
        if not node:
            return
        self._inorder(node.left, result)
        result.append(node.val)
        self._inorder(node.right, result)

    def rebuild_with_new_root(self, new_root_node):
        all_values = self.inorder_traversal(self.root)
        all_values.remove(new_root_node.val)
        random.shuffle(all_values)
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

    def on_find_node(self):
        popup = tk.Toplevel(self.canvas.winfo_toplevel())
        popup.title("Find Node")
        popup.geometry("300x140")
        popup.transient(self.canvas.winfo_toplevel())
        popup.grab_set()
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        popup.geometry(f"+{x}+{y}")
        tk.Label(popup, text="Enter node value to find:", font=("Arial", 12)).pack(fill="x", padx=10, pady=(15, 5))
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(fill="x", padx=10, pady=(0, 10))
        value_entry.focus_set()
        warning_label = tk.Label(popup, text="", fg="red", font=("Arial", 10))
        warning_label.pack(fill="x", padx=10, pady=(0, 2))
        def do_find():
            val = value_entry.get()
            try:
                value = int(val)
            except ValueError:
                warning_label.config(text="Please enter a valid integer.")
                return
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

    def update_tree_from_array(self, values):
        # Cho phép truyền vào list số nguyên hoặc chuỗi "1,2,3"
        if isinstance(values, str):
            values = [int(v.strip()) for v in values.split(",") if v.strip()]
        try:
            values = [int(v) for v in values]
        except Exception:
            tk.messagebox.showerror("Error", "Giá trị không hợp lệ!")
            return

        # Loại bỏ giá trị trùng lặp, giữ thứ tự xuất hiện đầu tiên
        unique_values = []
        for v in values:
            if v not in unique_values:
                unique_values.append(v)

        # Dựng lại BST đúng thứ tự chèn (KHÔNG sort!)
        root = None
        for v in unique_values:
            root = self.insert_bst(root, v)

        self.root = root
        self.draw_tree(self.root)
        if hasattr(self, "sidebar"):
            self.sidebar.tree_root = self.root
        if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
            arr = self.get_array_representation()
            self.sidebar.update_array_display(arr)
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
            # Lưu theo thứ tự chèn (nếu có), nếu không thì dùng preorder traversal
            def preorder(node, arr):
                if not node:
                    return
                arr.append(node.val)
                preorder(node.left, arr)
                preorder(node.right, arr)
            arr = []
            preorder(self.root, arr)
            content = ", ".join(str(v) for v in arr)

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
        if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
            arr = self.get_array_representation()
            self.sidebar.update_array_display(arr)
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

            # Hỗ trợ cả dạng "1,2,3" hoặc từng dòng một số
            if "," in content:
                values = [int(v.strip()) for v in content.split(",") if v.strip()]
            else:
                values = [int(line.strip()) for line in content.splitlines() if line.strip()]

            # Loại bỏ giá trị trùng lặp, giữ thứ tự xuất hiện đầu tiên
            unique_values = []
            for v in values:
                if v not in unique_values:
                    unique_values.append(v)

            # Dựng lại BST đúng thứ tự chèn
            root = None
            for v in unique_values:
                root = self.insert_bst(root, v)
            self.root = root
            self.draw_tree(self.root)

            # Cập nhật array trên sidebar bằng inorder (không dùng tree_to_array)
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "update_array_display"):
                arr = self.get_array_representation()
                self.sidebar.update_array_display(arr)
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                self.sidebar.show_toast_notification(f"Tree loaded from \n{file_path}")

        except Exception as e:
            if hasattr(self, "sidebar") and hasattr(self.sidebar, "show_toast_notification"):
                self.sidebar.show_toast_notification(f"Error loading file \n{e}")
            else:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", f"Error loading file \n{e}")