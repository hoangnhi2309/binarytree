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
            return  # Người dùng bấm Cancel

        from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
        from visualizer.bst_visualizer import BSTVisualizer
        from visualizer.avl_visualizer import AVLVisualizer

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            # Binary Tree: giữ nguyên
            result = []
            def dfs(node):
                if not node:
                    return
                left_val = node.left.val if node.left else 0
                right_val = node.right.val if node.right else 0
                result.append(f"{node.val}, {left_val}, {right_val}")
                dfs(node.left)
                dfs(node.right)
            dfs(self.tree_root)
            content = "\n".join(result)
        else:
            # BST/AVL: chỉ lưu các giá trị khác 0, dãy ngang
            array = self.tree_to_array(self.tree_root)
            filtered = [str(v) for v in array if v != 0]
            content = ", ".join(filtered)

        try:
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
                lines = f.readlines()

            node_map = {}
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                node_val = int(parts[0].strip())
                left_val = int(parts[1].strip())
                right_val = int(parts[2].strip())
                node_map[node_val] = (left_val, right_val)

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

            root_val = int(lines[0].strip().split(",")[0])
            root = get_node(root_val)

            self.tree_root = root

            # Vẽ lại cây
            self.visualizer.draw_tree(self.tree_root)

            # Cập nhật mảng nếu bạn cần
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
        from visualizer.avl_visualizer import AVLVisualizer

        if isinstance(self.visualizer, BinaryTreeVisualizer) and not isinstance(self.visualizer, (BSTVisualizer, AVLVisualizer)):
            label_text = "Tree Depth:"
            default_value = "3"
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

    def handle_create_tree(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            extra = int(self.depth_entry.get())  # depth hoặc số node tùy loại cây

            if min_val > max_val or extra <= 0:
                raise ValueError("Min > Max hoặc extra <= 0")

            # Gọi create_random_tree tùy theo loại visualizer
            vis = self.visualizer
            if vis is None:
                raise ValueError("Chưa có visualizer")

            # Tạo cây mới
            self.tree_root = vis.create_random_tree(min_val, max_val, extra)
            self.visualizer.set_root(self.tree_root)
            self.visualizer.draw_tree(self.tree_root)

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
                self.visualizer.root = self.tree_root  # Đảm bảo đồng bộ sau khi update!
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

            # Kiểm tra BST: inorder phải tăng dần
            if isinstance(self.visualizer, BSTVisualizer):
                for i in range(1, len(new_vals)):
                    if new_vals[i] <= new_vals[i-1]:
                        self.show_toast_notification("Error: BST values must be strictly increasing (inorder).")
                        return

            # Kiểm tra AVL: inorder phải tăng dần và sau khi cập nhật phải rebuild lại cây để đảm bảo cân bằng
            if isinstance(self.visualizer, AVLVisualizer):
                for i in range(1, len(new_vals)):
                    if new_vals[i] <= new_vals[i-1]:
                        self.show_toast_notification("Error: AVL values must be strictly increasing (inorder).")
                        return
                # Xây lại cây AVL từ đầu để đảm bảo cân bằng
                root = None
                for val in new_vals:
                    root = self.visualizer.insert_avl(root, val)
                self.tree_root = root
                self.visualizer.set_root(self.tree_root)
                self.visualizer.draw_tree(self.tree_root)
                self.array = self.tree_to_array(self.tree_root)
                self.update_array_display(self.array)
                self.show_toast_notification("AVL tree rebuilt successfully.")
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

    def set_visualizer(self, visualizer):
        self.visualizer = visualizer
        self.controller = Controller(self.visualizer, self)
        self.visualizer.controller = self.controller


def setup_visualizer(visualizer_class, sidebar, right_frame):
    visualizer = visualizer_class(right_frame)
    visualizer.sidebar = sidebar  # Thiết lập sidebar cho visualizer
    sidebar.visualizer = visualizer  # Thiết lập visualizer cho sidebar
    return visualizer

def on_sidebar_button_click(sidebar, visualizer_class, right_frame):
    # Xóa visualizer cũ nếu có
    if sidebar.visualizer:
        sidebar.visualizer.clear_canvas()

    # Thiết lập visualizer mới
    visualizer = setup_visualizer(visualizer_class, sidebar, right_frame)

    # Tạo cây mẫu và vẽ
    sample_tree = TreeNode(1)
    sample_tree.left = TreeNode(2)
    sample_tree.right = TreeNode(3)
    sample_tree.left.left = TreeNode(4)
    sample_tree.left.right = TreeNode(5)

    sidebar.tree_root = sample_tree
    visualizer.set_root(sample_tree)
    visualizer.draw_tree(sample_tree)

    # Cập nhật lại array display
    array_representation = sidebar.tree_to_array(sample_tree)
    sidebar.update_array_display(array_representation)

from visualizer.binary_tree_visualizer import BinaryTreeVisualizer

def on_binary_tree_click(sidebar, right_frame):
    on_sidebar_button_click(sidebar, BinaryTreeVisualizer, right_frame)

from visualizer.bst_visualizer import BSTVisualizer

def on_bst_click(sidebar, right_frame):
    on_sidebar_button_click(sidebar, BSTVisualizer, right_frame)

from visualizer.avl_visualizer import AVLVisualizer

def on_avl_click(sidebar, right_frame):
    on_sidebar_button_click(sidebar, AVLVisualizer, right_frame)