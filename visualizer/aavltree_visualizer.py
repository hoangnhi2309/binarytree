import tkinter as tk
from tkinter import messagebox
import random
class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None
        self.height = 1  # Cần cho AVL
class AVLTree:
    def insert(self, root, key):
        if not root:
            return TreeNode(key)
        elif key < root.val:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)

        # Cập nhật chiều cao
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Kiểm tra hệ số cân bằng
        balance = self.get_balance(root)

        # Các trường hợp xoay
        if balance > 1 and key < root.left.val:
            return self.right_rotate(root)
        if balance < -1 and key > root.right.val:
            return self.left_rotate(root)
        if balance > 1 and key > root.left.val:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.val:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0
def insert_avl_node(self, value):
    if self.tree_root is None:
        self.tree_root = TreeNode(value)
    else:
        avl = AVLTree()
        self.tree_root = avl.insert(self.tree_root, value)
    self.root = self.tree_root
    self.draw_tree(self.root)
