import tkinter as tk
from tkinter import Label, Entry, Button
from core.services import TrainService

class RouteViewerInterface:
    """列车路线查看界面类"""
    
    def __init__(self, parent_window, utils, display_table_func, show_main_menu_func):
        """初始化路线查看界面
        
        Args:
            parent_window: 主窗口
            utils: GUI工具类实例
            display_table_func: 显示表格数据的函数
            show_main_menu_func: 返回主菜单的函数
        """
        self.parent = parent_window
        self.utils = utils
        self.display_table = display_table_func
        self.show_main_menu = show_main_menu_func
    
    def show_train_route_frame(self):
        """显示列车路线查询界面"""
        self.utils.clear_frame(self.parent)
        Label(self.parent, text="Train Route Query", font=("Arial", 14)).pack(pady=10)
        
        # 列车号输入
        Label(self.parent, text="Train Number:").pack()
        train_number_entry = Entry(self.parent)
        train_number_entry.insert(0, "G1")
        train_number_entry.pack(pady=5)
        
        # 日期输入（可选）
        Label(self.parent, text="Date (YYYY-MM-DD, optional):").pack()
        date_entry = Entry(self.parent)
        date_entry.pack(pady=5)
        
        def query_route():
            train_number = train_number_entry.get().strip()
            departure_date = date_entry.get().strip()
            
            if not train_number:
                self.utils.show_error("Error", "Please enter train number")
                return
            
            # 验证日期格式
            if not self.utils.validate_date(departure_date):
                self.utils.show_error("Error", "Invalid date format. Please use YYYY-MM-DD format")
                return
                
            self.display_table(
                lambda: TrainService.get_train_route(
                    train_number, 
                    departure_date if departure_date else None
                ),
                ["Train", "Start_date", "Station", "Code", "Arrival", "Departure", 
                "Type", "Order", "Sold_tickets"],
                window_size="1000x400",
            )
        
        Button(self.parent, text="Query Route", 
            command=query_route).pack(pady=10)
        
        Button(self.parent, text="Back to Main Menu", 
            command=self.show_main_menu).pack(pady=20)