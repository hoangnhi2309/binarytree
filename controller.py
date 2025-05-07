import tkinter.messagebox as messagebox
class Controller:
    def __init__(self, visualizer, sidebar):
        self.visualizer = visualizer
        self.sidebar = sidebar
        self.tree_root = None


    def show_result(self, result_str):
        # Hiển thị kết quả duyệt cây
        print(result_str)
        messagebox.showinfo("Kết quả Duyệt Cây", result_str)  # Hiển thị trong cửa sổ thông báo

