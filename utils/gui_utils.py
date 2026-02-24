import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button
import datetime

class GUIUtils:
    """GUI工具类，提供通用的GUI操作函数"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
    def clear_frame(self, frame):
        """清空框架中的所有组件"""
        for widget in frame.winfo_children():
            widget.destroy()
    
    def center_window(self, window):
        """窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def create_modal_window(self, title, geometry="400x300"):
        """创建模态子窗口"""
        window = Toplevel(self.main_window)
        window.withdraw()  # 初始隐藏
        window.title(title)
        window.geometry(geometry)
        window.transient(self.main_window)  # 设置为父窗口的子窗口
        window.grab_set()  # 设置为模态窗口
        
        # 窗口居中
        window.update_idletasks()
        self.center_window(window)
        
        # 显示窗口
        window.deiconify()
        
        return window
    
    def show_message(self, title, message):
        """显示信息消息"""
        message_window = self.create_modal_window(title, "300x150")
        Label(message_window, text=message, wraplength=250).pack(pady=20)
        Button(message_window, text="OK", command=message_window.destroy).pack(pady=10)
    
    def show_error(self, title, message):
        """显示错误消息"""
        error_window = self.create_modal_window(title, "300x150")
        Label(error_window, text=message, wraplength=250).pack(pady=20)
        Button(error_window, text="OK", command=error_window.destroy).pack(pady=10)
    
    def show_confirmation(self, title, message):
        """显示确认对话框"""
        confirm_window = self.create_modal_window(title, "300x150")
        result = [False]  # 使用列表存储结果
        
        def on_yes():
            result[0] = True
            confirm_window.destroy()
            
        def on_no():
            result[0] = False
            confirm_window.destroy()
        
        Label(confirm_window, text=message, wraplength=250).pack(pady=20)
        
        button_frame = tk.Frame(confirm_window)
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Yes", command=on_yes).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="No", command=on_no).pack(side=tk.LEFT, padx=10)
        
        confirm_window.wait_window()  # 等待窗口关闭
        return result[0]
    
    @staticmethod
    def validate_date(date_str):
        """验证日期格式是否正确"""
        if not date_str:  # 允许为空
            return True
            
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False