import tkinter as tk
import tkinter.ttk as ttk
import random
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import os
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from controller import Controller
import ast
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
        self.visualizer = BinaryTreeVisualizer(self)
        self.controller = Controller(self.visualizer, self)
        self.visualizer.controller = self.controller
        self.pack(side="left", fill="y")
        self.pack_propagate(False)

        self.notification_label = tk.Label(self.master, text="", bg="green", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.notification_label.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")  # Đặt ở góc phải trên

        self.array = []
        self.highlighted_node = None # <-- OK vì giờ đã có trong đối số

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
#tạo button 
        self.create_random_tree_btn = self.create_modern_button("Create random tree", self.on_random_tree)
        self.create_modern_button("Apply changes", self.apply_array_edit)
        self.create_modern_button("Delete tree", self.on_clear_tree)
        # self.create_modern_button("Traversal", self.show_traversal_options)
        self.create_modern_button("Save to file", self.save_tree_to_file)
        self.create_modern_button("Load from file", self.load_tree_from_file)
    
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
        self.array_display.insert("1.0", self.format_array_multiline(array))

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
        self.popup.transient(self.winfo_toplevel())  # Popup nằm giữa cửa sổ chính

        # Min Value
        tk.Label(self.popup, text="Min Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.min_entry.insert(0, "1")
        self.min_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Max Value
        tk.Label(self.popup, text="Max Value:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.max_entry.insert(0, "99")
        self.max_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Tree Depth
        tk.Label(self.popup, text="Tree Depth:", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        self.depth_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.depth_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.depth_entry.insert(0, "3")

        # Frame chứa 2 nút Create và Cancel căn phải
        button_frame = tk.Frame(self.popup)
        button_frame.pack(pady=10, padx=10, fill="x")

        # Spacer để đẩy nút sang phải
        tk.Label(button_frame).pack(side="left", expand=True)
        # Nút Cancel (màu đỏ)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.popup.destroy, font=("Arial", 12), bg="grey", fg="black")
        cancel_button.pack(side="right", padx=(0, 5))
        # Nút Create
        create_button = tk.Button(button_frame, text="Create", command=self.create_tree, font=("Arial", 12), bg="grey")
        create_button.pack(side="right", padx=(5, 0))

        # Gắn sự kiện cập nhật depth tối đa
        self.min_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())
        self.max_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())
        self.update_max_depth_hint()

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
    
    def traverse_tree(self, root, mode):
        # Hàm duyệt cây theo mode (preorder, inorder, postorder)
        if root is None:
            return []

        if mode == "preorder":
            return [root.val] + self.traverse_tree(root.left, mode) + self.traverse_tree(root.right, mode)
        elif mode == "inorder":
            return self.traverse_tree(root.left, mode) + [root.val] + self.traverse_tree(root.right, mode)
        elif mode == "postorder":
            return self.traverse_tree(root.left, mode) + self.traverse_tree(root.right, mode) + [root.val]
        else:
            return []
        
    def show_traversal_options(self):
        if not self.tree_root:
            messagebox.showwarning("Warning", "Tree is empty. Please create or load a tree.")
            return

        def on_select(mode):
            result = self.traverse_tree(self.tree_root, mode)
            result_str = " -> ".join(map(str, result))
            # Thêm tên loại duyệt vào thông báo
            messagebox.showinfo(f"{mode.capitalize()} Traversal", f"{mode.capitalize()} Traversal: {result_str}")

        # Tạo cửa sổ popup
        popup = tk.Toplevel(self)
        popup.title("Choose Traversal Method")
        popup.geometry("300x250")  # Tăng kích thước cửa sổ nếu cần
        popup.config(bg="#f7f7f7")  # Màu nền sáng cho cửa sổ

        # Tiêu đề cửa sổ
        tk.Label(popup, text="Select Traversal Type:", font=("Arial", 14, "bold"), bg="#f7f7f7").pack(pady=20)

        # Định dạng nút bấm
        button_style = {
            "font": ("Arial", 12),
            "bg": "#4CAF50",  # Màu nền nút
            "fg": "black",  # Màu chữ
            "relief": "raised",  # Đường viền nổi cho nút
            "bd": 0,  # Độ dày đường viền
            "width": 20,
            "height": 2,
            "activebackground": "#45a049",  # Màu nền khi hover
            "activeforeground": "white",  # Màu chữ khi hover
            "highlightbackground": "black",  # Viền đen khi có focus
            "highlightthickness": 2  # Độ dày viền khi có focus
        }

        # Hàm để thay đổi màu nền khi di chuột qua
        def on_enter(e): e.widget.config(bg="#45a049")
        def on_leave(e): e.widget.config(bg="#4CAF50")

        postorder_button = tk.Button(self.popup, text="Postorder", command=lambda: [on_select("postorder"), self.popup.destroy()], **button_style)
        postorder_button.pack(pady=10)
        postorder_button.bind("<Enter>", lambda e: on_enter(e, postorder_button))  # Khi di chuột qua nút
        postorder_button.bind("<Leave>", lambda e: on_leave(e, postorder_button))  # Khi chuột rời khỏi nút

        # Thêm khung vào Sidebar
        bordered_frame = tk.Frame(self, bg="white", highlightbackground="black", highlightthickness=1)
        bordered_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Thêm nội dung vào khung
        bordered_label = tk.Label(
            bordered_frame,
            text="This is a bordered frame",
            font=("Arial", 12),
            bg="white",
            fg="black"
        )
        bordered_label.pack(pady=10)

    #     # Tạo các nút lựa chọn duyệt cây
        preorder_button = tk.Button(popup, text="Preorder", command=lambda: [on_select("preorder"), popup.destroy()], **button_style)
        preorder_button.pack(pady=10)
        preorder_button.bind("<Enter>", lambda e: on_enter(e, preorder_button))  # Khi di chuột qua nút
        preorder_button.bind("<Leave>", lambda e: on_leave(e, preorder_button))  # Khi chuột rời khỏi nút

        inorder_button = tk.Button(popup, text="Inorder", command=lambda: [on_select("inorder"), popup.destroy()], **button_style)
        inorder_button.pack(pady=10)
        inorder_button.bind("<Enter>", lambda e: on_enter(e, inorder_button))  # Khi di chuột qua nút
        inorder_button.bind("<Leave>", lambda e: on_leave(e, inorder_button))  # Khi chuột rời khỏi nút

        postorder_button = tk.Button(popup, text="Postorder", command=lambda: [on_select("postorder"), popup.destroy()], **button_style)
        postorder_button.pack(pady=10)
        postorder_button.bind("<Enter>", lambda e: on_enter(e, postorder_button))  # Khi di chuột qua nút
        postorder_button.bind("<Leave>", lambda e: on_leave(e, postorder_button))  # Khi chuột rời khỏi nút

    #     # Tạo nút đóng (Close)
        close_button = tk.Button(popup, text="Close", command=lambda: popup.destroy(), font=("Arial", 12), bg="#f44336", fg="white", relief="raised", bd=2, width=20, height=2)
        close_button.pack(pady=10)

    def show_traversal_options(self):
        popup = tk.Toplevel(self)
        popup.title("Choose Traversal Method")
        popup.geometry("300x250")  # Adjust size as needed
        popup.config(bg="#f7f7f7")  # Background color for the popup

        popup.grab_set()

    def apply_array_edit(self):
        text = self.array_display.get("1.0", "end").strip()
        lines = text.split("\n")
        new_data = []
        all_vals = set()  # lưu tất cả node cần tạo

        for line in lines:
            parts = line.split(",")
            if len(parts) != 3:
                continue
            try:
                val = int(parts[0].strip())
                left = int(parts[1].strip())
                right = int(parts[2].strip())
                new_data.append((val, left, right))
                all_vals.add(val)
                if left != 0:
                    all_vals.add(left)
                if right != 0:
                    all_vals.add(right)
            except ValueError:
                continue

        if not new_data:
            self.show_toast_notification("Không có dữ liệu hợp lệ.")
            return

        # Tạo tất cả các node
        nodes = {val: TreeNode(val) for val in all_vals}

        # Liên kết left, right
        for val, left, right in new_data:
            node = nodes[val]
            node.left = nodes.get(left) if left != 0 else None
            node.right = nodes.get(right) if right != 0 else None

        # Tìm root: node không phải con ai cả
        children = set()
        for _, left, right in new_data:
            if left != 0:
                children.add(left)
            if right != 0:
                children.add(right)

        possible_roots = [val for val in all_vals if val not in children]

        if not possible_roots:
            self.show_toast_notification("Không tìm thấy node root hợp lệ.")
            return

        root_val = possible_roots[0]
        if len(possible_roots) > 1:
            self.show_toast_notification("Cảnh báo: Nhiều node root, chọn node đầu tiên.")

        self.tree_root = nodes[root_val]
        self.visualizer.draw_tree(self.tree_root)

        # Cập nhật lại array
        self.array = self.tree_to_array(self.tree_root)
        self.update_array_display(self.array)

        self.show_toast_notification("Đã cập nhật lại cây từ bảng.")

    def set_visualizer(self, visualizer):
        self.visualizer = visualizer
        # Đổi tên nút nếu là BST
        if visualizer.__class__.__name__ == "BSTVisualizer":
            self.create_random_tree_btn.config(text="Create tree")
        else:
            self.create_random_tree_btn.config(text="Create random tree")

