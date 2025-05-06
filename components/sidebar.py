import tkinter as tk
import tkinter.ttk as ttk
import random
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import os
from visualizer.binary_tree_visualizer import BinaryTreeVisualizer
from controller import Controller

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="grey", width=400)
         # Khởi tạo visualizer và controller
        self.visualizer = BinaryTreeVisualizer(self)
        self.controller = Controller(self.visualizer, self)
        self.visualizer.controller = self.controller  # Gán controller cho visualizer
        self.pack(side="left", fill="y")
        self.pack_propagate(False)
        self.tree_root = None
        self.array = []
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
#tạo button 
        self.create_modern_button("Create random tree", self.on_random_tree)
        self.create_modern_button("Delete tree", self.on_clear_tree)
        self.create_modern_button("Traversal", self.show_traversal_options)
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
 # Tạo popup để nhập min, max và độ sâu
        self.popup = tk.Toplevel(self)  # Lưu popup vào self.popup
        self.popup.title("Create Random Tree")
        self.popup.geometry("300x250")
        self.popup.transient(self.winfo_toplevel())  # Hiển thị popup ở giữa cửa sổ chính

        tk.Label(self.popup, text="Min Value:", font=("Arial", 12)).pack(pady=5)
        self.min_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.min_entry.insert(0, "1")  # Giá trị mặc định là 1
        self.min_entry.pack(pady=5)

        tk.Label(self.popup, text="Max Value:", font=("Arial", 12)).pack(pady=5)
        self.max_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.max_entry.insert(0, "99")  # Giá trị mặc định là 99
        self.max_entry.pack(pady=5)

        tk.Label(self.popup, text="Tree Depth:", font=("Arial", 12)).pack(pady=5)
        self.depth_entry = tk.Entry(self.popup, font=("Arial", 12))
        self.depth_entry.pack(pady=5)

        tk.Button(self.popup, text="Create", command=self.create_tree, font=("Arial", 12)).pack(pady=10)
 # Gắn sự kiện để tự động tính depth tối đa khi thay đổi Min/Max
        self.min_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())
        self.max_entry.bind("<KeyRelease>", lambda e: self.update_max_depth_hint())

        self.update_max_depth_hint()  # Cập nhật ban đầu
    
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
            self.tree_root = self.build_tree_from_list(self.array)

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

    def update_max_depth_hint(self):
            try:
                min_value = int(self.min_entry.get())
                max_value = int(self.max_entry.get())
                available_values = max_value - min_value + 1

                # Tính độ sâu tối đa
                max_depth = 0
                while (2**max_depth - 1) <= available_values:
                    max_depth += 1
                max_depth -= 1

                # Hiển thị gợi ý
                self.depth_entry.delete(0, tk.END)
                self.depth_entry.insert(0, str(max_depth))
            except ValueError:
                pass 

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
    
    def show_traversal_options(self):
        visualizer = self.controller.visualizer
        if not self.visualizer or not self.visualizer.tree_root:
            messagebox.showwarning("Chưa có cây", "Vui lòng tạo cây trước.")
            return

        popup = tk.Toplevel(self)
        popup.title("Chọn cách duyệt cây")
        popup.geometry("300x200")
        popup.transient(self.winfo_toplevel())

        tk.Button(popup, text="Duyệt tiền thứ tự (Pre-order)", font=("Arial", 12),
                  command=lambda: self.execute_traversal("preorder", popup)).pack(pady=5, fill="x", padx=20)

        tk.Button(popup, text="Duyệt trung thứ tự (In-order)", font=("Arial", 12),
                  command=lambda: self.execute_traversal("inorder", popup)).pack(pady=5, fill="x", padx=20)

        tk.Button(popup, text="Duyệt hậu thứ tự (Post-order)", font=("Arial", 12),
                  command=lambda: self.execute_traversal("postorder", popup)).pack(pady=5, fill="x", padx=20)
    def execute_traversal(self, mode, popup):
        visualizer = self.controller.visualizer  # Lấy lại visualizer mới nhất
        if visualizer and visualizer.tree_root:
            result = visualizer.traverse_tree(visualizer.tree_root, mode)
            result_str = " → ".join(map(str, result))
            self.controller.show_result("Kết quả duyệt " + mode + ": " + result_str)
            popup.destroy()
        else:
            messagebox.showinfo("Thông báo", "Vui lòng tạo cây trước khi duyệt.")
            # popup.destroy()  # có thể giữ lại để user đọc message
