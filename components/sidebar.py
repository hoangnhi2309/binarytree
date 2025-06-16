import tkinter as tk
import tkinter.ttk as ttk
import random
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import os
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from controller import Controller
from tkinter.filedialog import askopenfilename
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
class Sidebar(tk.Frame):
    def __init__(self, parent, show_status=None):
        super().__init__(parent, bg="grey", width=400)
        self.master = parent
        self.show_status = show_status 
        self.tree_root = None
        self.array = []
        self.visualizer = BinaryTreeVisualizer(self)
        self.controller = Controller(self.visualizer, self)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)

        self.notification_label = tk.Label(self.master, text="", bg="green", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.notification_label.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")
        array_label = tk.Label(self, text="Array:", font=("Arial", 20, "bold"), bg="grey", fg="black")
        array_label.pack(anchor="w", padx=20, pady=(0, 5))
        array_frame = tk.Frame(self, bg="grey")
        array_frame.pack(padx=20, pady=10, fill="both", expand=False)
        # Thêm frame chứa nút zoom
        zoom_frame = tk.Frame(self, bg="grey")
        zoom_frame.pack(pady=10)
        zoom_in_btn = tk.Label(
            zoom_frame,
            text="Zoom +",
            font=("Arial", 14),
            bg="#ffffff",
            fg="#333333",
            bd=2,
            cursor="hand2"
        )
        zoom_in_btn.pack(side="left", padx=5, pady=0, fill="x")
        zoom_in_btn.bind("<Enter>", lambda e: zoom_in_btn.config(bg="#e0e0e0"))
        zoom_in_btn.bind("<Leave>", lambda e: zoom_in_btn.config(bg="white"))
        zoom_in_btn.bind("<Button-1>", lambda e: self.visualizer.zoom_in() if self.visualizer else None)
        zoom_out_btn = tk.Label(
            zoom_frame,
            text="Zoom -",
            font=("Arial", 14),
            bg="#ffffff",
            fg="#333333",
            bd=2,
            cursor="hand2"
        )
        zoom_out_btn.pack(side="left", padx=5, pady=0, fill="x")
        zoom_out_btn.bind("<Enter>", lambda e: zoom_out_btn.config(bg="#e0e0e0"))
        zoom_out_btn.bind("<Leave>", lambda e: zoom_out_btn.config(bg="white"))
        zoom_out_btn.bind("<Button-1>", lambda e: self.visualizer.zoom_out() if self.visualizer else None)
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
        # Các nút bấm
        self.create_modern_button("Create random tree", self.on_random_tree)
        self.create_modern_button("Update tree", self.update_edit)
        self.create_modern_button("Delete tree", self.on_clear_tree)
        self.create_modern_button("Save to file", self.save_tree_to_file)
        self.create_modern_button("Load from file", self.load_tree_from_file)
    def create_modern_button(self, text, command):
        btn = tk.Button(self, text=text, command=command, font=("Arial", 12), bg="grey", fg="white")
        btn.pack(pady=5, padx=10, fill="x")
        return btn
    def reset_state(self):
        # Xóa dữ liệu cây, mảng, thông tin...
        self.tree_root = None
        self.array = []
        # Xóa nội dung trong Text widget array_display
        self.array_display.config(state="normal")
        self.array_display.delete("1.0", tk.END)
        self.array_display.config(state="disabled")
    def clear_tree(self):
        # Xóa cây trong bộ nhớ
        self.tree_root = None
        # Xóa dữ liệu hiển thị mảng (nếu chưa xóa)
        self.array = []
        self.update_array_display()  # hàm bạn dùng để cập nhật mảng trong giao diện
        # Xóa canvas vẽ cây (phải có hàm clear_canvas trong Visualizer)
        if self.visualizer:
            self.visualizer.clear_canvas()
    def format_array_multiline(self, array):
        lines = []
        for i, val in enumerate(array):
            if val == 0:
                continue  # Bỏ qua nếu node cha là rỗng
            left = array[2 * i + 1] if 2 * i + 1 < len(array) and array[2 * i + 1] != 0 else "0"
            right = array[2 * i + 2] if 2 * i + 2 < len(array) and array[2 * i + 2] != 0 else "0"
            lines.append(f"{val}, {left}, {right}")
        return "\n".join(lines)
    def update_array_display(self, array):
        self.array_display.config(state="normal")
        self.array_display.delete("1.0", tk.END)
        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer
        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            text = self.format_array_multiline(array)
        else:
            # Lọc bỏ các số 0 (node rỗng) cho BST/AVL
            filtered = [v for v in array if v != 0]
            text = ", ".join(map(str, filtered))
        self.array_display.insert("1.0", text)
        # Đừng đặt state="disabled" ở đây, để người dùng sửa trực tiếp
    def tree_to_array(self, root):
        if not root:
            return []
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
        # Bỏ các 0 dư thừa cuối mảng
        while result and result[-1] == 0:
            result.pop()
        return result
    def save_tree_to_file(self):
        if not self.tree_root:
            self.show_toast_notification("No tree to save.")
            return

        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Tree As"
        )
        if not file_path:
            return

        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer

        try:
            if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
                result = []
                queue = [self.tree_root]

                while queue:
                    current = queue.pop(0)
                    if not current:
                        continue

                    left_val = current.left.val if current.left else 0
                    right_val = current.right.val if current.right else 0
                    result.append(f"{current.val}, {left_val}, {right_val}")

                    queue.append(current.left)
                    queue.append(current.right)

                content = "\n".join(result)
            else:
                # Với BST / AVL
                array = self.tree_to_array(self.tree_root)
                filtered = [str(v) for v in array if v != 0]
                content = ", ".join(filtered)

            with open(file_path, "w") as f:
                f.write(content)

            self.show_toast_notification(f"Tree successfully saved to \n{file_path}")

        except Exception as e:
            self.show_toast_notification(f"Error saving file \n{e}")


    def show_toast_notification(self, message, duration=3000):
        toast = tk.Toplevel(self.master)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        width = 400
        screen_width = toast.winfo_screenwidth()
        x = screen_width - width - 10
        y = 100
        # Tạo frame chứa label, thêm padding rõ ràng
        frame = tk.Frame(toast, bg="grey", padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        label = tk.Label(
            frame,
            text=message,
            bg="grey",
            fg="black",
            font=("Arial", 16),
            wraplength=width - 40,
            justify="left",
            anchor="nw"  # căn trái
        )
        label.pack(fill="both", expand=True)
    # Cập nhật để đo chiều cao chính xác
        label.update_idletasks()
        height = label.winfo_reqheight() + 20
        toast.geometry(f"{width}x{height}+{x}+{y}")
        toast.after(duration, toast.destroy)

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
            if isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
                # Hỗ trợ cả dạng "1,2,3" hoặc từng dòng một số
                if "," in content:
                    values = [int(v.strip()) for v in content.split(",") if v.strip()]
                else:
                    values = [int(line.strip()) for line in content.splitlines() if line.strip()]
                self.visualizer.update_tree_from_array(values)
                self.tree_root = self.visualizer.root
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
            # Gán left và right theo thứ tự dòng
            for i, (val, l_val, r_val) in enumerate(node_list):
                node = tree_nodes[i]
                if l_val != 0:
                    node.left = next((n for n in tree_nodes if n.val == l_val and n != node and n != node.right), TreeNode(l_val))
                if r_val != 0:
                    node.right = next((n for n in tree_nodes if n.val == r_val and n != node and n != node.left), TreeNode(r_val))

            root = tree_nodes[0]
            self.tree_root = root
            self.visualizer.set_root(root)
            self.visualizer.draw_tree(self.tree_root)
            array_representation = self.tree_to_array(self.tree_root)
            self.update_array_display(array_representation)
            self.show_toast_notification(f"Tree loaded from \n{file_path}")

        except Exception as e:
            self.show_toast_notification(f"Error loading file \n{e}")
    def on_search_node(self):
        value = self.search_entry.get()
        if value.isdigit():
            value = int(value)
            # Tìm node trong cây (không kiểm tra trong self.array nữa)
            self.highlighted_node = self._find_node(self.tree_root, value)
            if self.highlighted_node:
                if self.visualizer:
                    self.visualizer.highlighted_node = self.highlighted_node
                    self.visualizer.scroll_to_node(self.highlighted_node)
                    self.visualizer.draw_tree(self.tree_root)
            else:
                self.show_toast_notification(f"No valid node found {value}.")
        else:
            self.show_toast_notification("Please enter a valid integer.")
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
            # Nếu popup đã mở thì không mở thêm
        if hasattr(self, "popup") and self.popup and tk.Toplevel.winfo_exists(self.popup):
            self.popup.lift()
            self.popup.focus_force()
            return
        self.popup = tk.Toplevel(self)
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.winfo_toplevel())
        self.popup.grab_set()  # Modal: khóa cửa sổ cha cho đến khi đóng popup    self.popup.grab_set()  # Modal: khóa cửa sổ cha cho đến khi đóng popup
        self.popup.focus_force()  
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

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            label_text = "Tree Depth:"
            default_value = "3"
            tk.Label(self.popup, text=label_text, font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
            # Thêm label cảnh báo
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
        create_button = tk.Button(button_frame, text="Create", command=self.handle_create_tree, font=("Arial", 12), bg="grey")
        create_button.pack(side="right", padx=(5, 0))
        self.popup.bind("<Return>", lambda e: self.handle_create_tree())
    def handle_create_tree(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            extra = int(self.depth_entry.get())  # depth hoặc số node tùy loại cây
            if min_val > max_val or extra <= 0:
                raise ValueError("Min > Max hoặc extra <= 0")
            vis = self.visualizer
            if vis is None:
                raise ValueError("Chưa có visualizer")

            from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
            from visualizer.bst_visualizer import BSTVisualizer
            from visualizer.avl_visualizer import AVLVisualizer

            if isinstance(vis, BinaryTreeVisualizer) and not isinstance(vis, (BSTVisualizer, AVLVisualizer)):
                # Binary Tree: random array + dựng cây theo level-order
                arr = vis.generate_random_tree_array(min_val, max_val, extra)
                tree_root = vis.array_to_tree_level_order(arr)
                vis.set_root(tree_root)
                vis.draw_tree(tree_root)
                self.tree_root = tree_root
            else:
                # BST/AVL: dùng create_random_tree như cũ
                tree_root = vis.create_random_tree(min_val, max_val, extra)
                vis.set_root(tree_root)
                vis.draw_tree(tree_root)
                self.tree_root = tree_root

            # Cập nhật mảng nếu có
            if hasattr(self, "tree_to_array") and hasattr(self, "update_array_display"):
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)
            self.popup.destroy()
        except Exception as e:
            print("DEBUG ERROR:", e)
            tk.messagebox.showerror("Lỗi", "Thông số không hợp lệ hoặc không tạo được cây.")
    def create_tree(self):
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
            # Tạo danh sách giá trị và sắp xếp
            self.array = sorted(self.generate_random_tree_array(min_value, max_value, depth))
            print(f"Generated Sorted Array: {self.array}")
            # Xây dựng cây từ danh sách đã sắp xếp
            self.tree_root = self.build_random_tree(self.array.copy(), 1, depth)
            if self.tree_root:  # Kiểm tra nếu cây đã được tạo
                if self.visualizer:
                    self.visualizer.set_root(self.tree_root)  # Gán cây vào visualizer
                    self.visualizer.draw_tree(self.tree_root)  # Vẽ cây
                    new_array = self.visualizer.tree_to_array(self.tree_root)  # Cập nhật lại array
                    self.array = new_array
                    self.update_array_display(new_array)
                print("Tree has been successfully created.")
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
            if 2 * i + 1 < len(lst):
                nodes[i].left = nodes[2 * i + 1]
            if 2 * i + 2 < len(lst):
                nodes[i].right = nodes[2 * i + 2]
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
        return btn  # <-- Thêm dòng này
    
    def update_edit(self):
        text = self.array_display.get("1.0", "end").strip()
        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            node_map = {}

            for line in lines:
                parts = line.split(",")
                if len(parts) != 3:
                    self.show_toast_notification("Each line must have exactly 3 values: val, left, right.")
                    return
                try:
                    val = int(parts[0].strip())
                    left = int(parts[1].strip())
                    right = int(parts[2].strip())
                    if val in node_map:
                        self.show_toast_notification(f" Node {val} duplicated.")
                        return
                    node_map[val] = (left, right)
                except ValueError:
                    self.show_toast_notification("All values ​​must be integers.")
                    return


            if not node_map:
                self.show_toast_notification("There is no data to update.")
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
                self.show_toast_notification("Error determining root node.")
                return

            # Giữ lại các node còn liên kết từ root
            linked = set()
            def dfs(n):
                if n and n.val not in linked:
                    linked.add(n.val)
                    dfs(n.left)
                    dfs(n.right)
            dfs(root)

            # Cập nhật cây và visual
            self.tree_root = root
            self.visualizer.set_root(root)
            self.visualizer.draw_tree(root)

            # Tạo lại array chỉ chứa các node hợp lệ
            def array_from_tree(node):
                result = []
                queue = [node]
                visited = set()
                while queue:
                    n = queue.pop(0)
                    if n and n.val not in visited:
                        visited.add(n.val)
                        left_val = n.left.val if n.left else 0
                        right_val = n.right.val if n.right else 0
                        result.append(f"{n.val}, {left_val}, {right_val}")
                        queue.append(n.left)
                        queue.append(n.right)
                return "\n".join(result)

            self.array_display.config(state="normal")
            self.array_display.delete("1.0", "end")
            self.array_display.insert("1.0", array_from_tree(root))

            orphans = set(node_map.keys()) - linked
            if orphans:
                self.show_toast_notification(f"Automatically removed unlinked nodes: {sorted(orphans)}")
            else:
                self.show_toast_notification("Tree update successful.")
        elif isinstance(self.visualizer, BSTVisualizer) or isinstance(self.visualizer, AVLVisualizer):
            # Lấy dữ liệu từ array_display (cho phép nhập "1,2,3,4" hoặc từng dòng)
            text = self.array_display.get("1.0", "end").strip()
            if "," in text:
                values = [v.strip() for v in text.split(",") if v.strip()]
            else:
                values = [v.strip() for v in text.split("\n") if v.strip()]
            try:
                values = [int(v) for v in values]
            except Exception:
                self.show_toast_notification("Invalid value!")
                return

            # Gọi hàm update_tree_from_array của BSTVisualizer
            self.visualizer.update_tree_from_array(values)
            self.tree_root = self.visualizer.root
            self.show_toast_notification("Tree update successful.")
            return
