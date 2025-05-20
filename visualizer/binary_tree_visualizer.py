import tkinter as tk
import tkinter.messagebox as messagebox
import random

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
        self.node_radius = 18 
        self.level_height = 60
        self.highlighted_node = None  
        self.nodes_positions = [] 
        self.root = None
        self.sidebar = None

    def set_controller(self, controller):
        self.controller = controller

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def bind_click_event(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<Button-2>", self.on_canvas_middle_click)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        for node_x, node_y, node in self.nodes_positions:
            if (node_x - self.node_radius <= x <= node_x + self.node_radius and
                node_y - self.node_radius <= y <= node_y + self.node_radius):
                self.show_node_menu(event, node)
                break

    def on_canvas_right_click(self, event):
        pass

    def on_canvas_middle_click(self, event):
        pass

    def show_node_menu(self, event, node):
        self.highlighted_node = node
        self.draw_tree(self.root)

        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Node", command=lambda: self.edit_node(node))
        menu.add_command(label="Delete Node", command=lambda: self.delete_node(node))
        add_menu = tk.Menu(menu, tearoff=0)
        add_menu.add_command(label="Left side", command=lambda: self.add_child_node(node, "left"))
        add_menu.add_command(label="Right side", command=lambda: self.add_child_node(node, "right"))
        menu.add_cascade(label="Add Node", menu=add_menu)
        menu.add_command(label="Switch Node", command=lambda: self.switch_node(node))
        menu.post(event.x_root, event.y_root)

    def draw_tree(self, root):
        self.canvas.delete("all")
        self.nodes_positions = []

        if root:
            max_depth = self.get_tree_depth(root)
            canvas_width = max(800, int(2 ** max_depth * self.node_radius * 1.5))
            canvas_height = (max_depth + 1) * self.level_height + 100
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

            start_x = canvas_width // 2
            x_offset = self.node_radius * (2 ** (max_depth - 1))* 0.8
            self._draw_subtree(root, start_x, 40, x_offset, 0)

            # 🛠 Quan trọng: Cập nhật lại scrollregion theo thực tế
            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.config(scrollregion=bbox)

    def _draw_subtree(self, node, x, y, x_offset, depth):
        if node.left:
            left_x = x - x_offset
            left_y = y + self.level_height
            self.canvas.create_line(x, y, left_x, left_y)
            self._draw_subtree(node.left, left_x, left_y, x_offset // 2, depth + 1)

        if node.right:
            right_x = x + x_offset
            right_y = y + self.level_height
            self.canvas.create_line(x, y, right_x, right_y)
            self._draw_subtree(node.right, right_x, right_y, x_offset // 2, depth + 1)

        color = "grey" if node == self.highlighted_node else "white"
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius, fill=color)
        self.canvas.create_text(x, y, text=str(node.val), font=("Arial", 12, "bold"))
        self.nodes_positions.append((x, y, node))

    def get_tree_depth(self, node):
        if not node:
            return 0
        return 1 + max(self.get_tree_depth(node.left), self.get_tree_depth(node.right))

    def scroll_to_node(self, node):
        for x, y, n in self.nodes_positions:
            if n == node:
                # Kích thước vùng vẽ (toàn bộ canvas)
                bbox = self.canvas.bbox("all")
                if not bbox:
                    return
                total_width = bbox[2]
                total_height = bbox[3]

                # Kích thước hiển thị canvas
                visible_width = self.canvas.winfo_width()
                visible_height = self.canvas.winfo_height()

                # Tính vị trí muốn scroll tới (đưa node ra giữa)
                x_target = max(min(x - visible_width // 2, total_width - visible_width), 0)
                y_target = max(min(y - visible_height // 2, total_height - visible_height), 0)

                # Scroll theo tỷ lệ (0.0 -> 1.0)
                self.canvas.xview_moveto(x_target / total_width)
                self.canvas.yview_moveto(y_target / total_height)
                break

    def tree_to_array(self, root):
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
                result.append(0)
        return result

    def edit_node(self, node):
        popup = tk.Toplevel(self.canvas)
        popup.title("Edit Node")
        popup.geometry("300x150")
        popup.transient(self.canvas.winfo_toplevel())

        tk.Label(popup, text="New Value:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)
        tk.Button(popup, text="Save", command=lambda: self.save_value(node, value_entry, popup), font=("Arial", 12)).pack(pady=10)

    def save_value(self, node, value_entry, popup):
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
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def add_child_node(self, node, direction):
        new_value = random.randint(1, 100)
        new_node = TreeNode(new_value)

        if direction == "left":
            if node.left is None:
                node.left = new_node
            else:
                messagebox.showwarning("Node Exists", "Left node already exists.")
                return
        elif direction == "right":
            if node.right is None:
                node.right = new_node
            else:
                messagebox.showwarning("Node Exists", "Right node already exists.")
                return

        self.draw_tree(self.root)
        if self.sidebar:
            new_array = self.tree_to_array(self.root)
            self.sidebar.array = new_array
            self.sidebar.update_array_display(new_array)

    def switch_node(self, node):
        popup = tk.Toplevel(self.canvas)
        popup.title("Switch Node")
        popup.geometry("300x200")
        popup.transient(self.canvas.winfo_toplevel())

        tk.Label(popup, text="Enter value of the node to switch with:", font=("Arial", 12)).pack(pady=10)
        value_entry = tk.Entry(popup, font=("Arial", 12))
        value_entry.pack(pady=10)

        tk.Button(popup, text="Switch", command=lambda: self.perform_switch(node, value_entry, popup), font=("Arial", 12)).pack(pady=10)

    def perform_switch(self, node, value_entry, popup):
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
            popup.destroy()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

    def find_node_by_value(self, root, value):
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

    def add_random_node(self, probability=3):
        """
        Add a random node based on the given probability.
        If a random number (0-9) is less than the probability, create two child nodes.
        Otherwise, create only a left child node.
        """
        random_value = random.randint(0, 9)
        if random_value < probability:
            self.create_two_child_nodes()
        else:
            self.create_left_child_node()

    def create_two_child_nodes(self):
        # Logic to create two child nodes
        print("Created two child nodes")

    def create_left_child_node(self):
        # Logic to create only a left child node
        print("Created left child node")

    def create_random_tree(self, probability=3, max_depth=5):
        """
        Create a random binary tree based on the given probability.
        If a random number (0-9) is less than the probability, create two child nodes.
        Otherwise, create only a left child node.
        """
        def add_nodes(node, depth):
            if depth >= max_depth:
                return
            random_value = random.randint(0, 9)
            if random_value < probability:
                # Create two child nodes
                left_child = self.create_node(parent=node, position="left")
                right_child = self.create_node(parent=node, position="right")
                add_nodes(left_child, depth + 1)
                add_nodes(right_child, depth + 1)
            else:
                # Create only a left child node
                left_child = self.create_node(parent=node, position="left")
                add_nodes(left_child, depth + 1)

        # Start with the root node
        root = self.create_node(value="Root")
        add_nodes(root, depth=0)

    def create_node(self, parent=None, position=None, value=None):
        """
        Create a single node in the binary tree.
        This is a placeholder method and should be implemented with actual logic.
        """
        print(f"Created node with value: {value}, parent: {parent}, position: {position}")
        # Replace this with actual node creation logic
        return {"value": value, "parent": parent, "position": position}

