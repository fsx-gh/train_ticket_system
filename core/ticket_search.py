import tkinter as tk
from tkinter import Label, Entry, Button
from core.services import TicketService, OrderService

class TicketSearchInterface:
    """票务查询界面类，处理列车查询和订票"""
    
    def __init__(self, parent_window, utils, display_table_func, show_main_menu_func):
        """初始化票务查询界面
        
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
    
    def show_search_trains_frame(self):
        """显示搜索列车界面"""
        self.utils.clear_frame(self.parent)
        Label(self.parent, text="Search Trains", font=("Arial", 14)).pack(pady=10)

        # 出发站
        Label(self.parent, text="Departure Station:").pack()
        dep_station_entry = Entry(self.parent)
        dep_station_entry.insert(0, "北京")
        dep_station_entry.pack(pady=5)

        # 到达站
        Label(self.parent, text="Arrival Station:").pack()
        arr_station_entry = Entry(self.parent)
        arr_station_entry.insert(0, "上海")
        arr_station_entry.pack(pady=5)

        # 出发日期
        Label(self.parent, text="Departure Date (YYYY-MM-DD):").pack()
        date_entry = Entry(self.parent)
        date_entry.pack(pady=5)
        
        def search_trains():
            dep_station = dep_station_entry.get()
            arr_station = arr_station_entry.get()
            departure_date = date_entry.get()

            # 验证日期格式
            if not self.utils.validate_date(departure_date):
                self.utils.show_error("Error", "Invalid date format. Please use YYYY-MM-DD format")
                return
            
            self.display_table(
                lambda: TicketService.search_available_tickets(
                    dep_station, arr_station, departure_date
                ),
                ["Train No", "Start Date", "From", "Departure Time", "To", "Arrival Time", 
                "Price", "Seats", "Type"],
                enable_booking=True,  # 启用订票功能
                window_size="1000x400",
            )

        Button(self.parent, text="Search", 
            command=search_trains).pack(pady=10)

        Button(self.parent, text="Back to Main Menu", 
            command=self.show_main_menu).pack(pady=20)
    
    def create_booking_window(self, train_info, name, id_card):
        """创建订票窗口"""
        booking_window = self.utils.create_modal_window(
            "Book Ticket",
            "500x350"
        )
        
        # 显示选中的车次信息 - 修正索引以匹配 TicketService.search_available_tickets 返回的数据结构
        Label(booking_window, text=f"Train: {train_info[0]}", font=("Arial", 12)).pack(pady=5)
        Label(booking_window, text=f"Date: {train_info[1]}", font=("Arial", 12)).pack(pady=5)
        Label(booking_window, text=f"From: {train_info[2]} -> To: {train_info[4]}", font=("Arial", 12)).pack(pady=5)
        Label(booking_window, text=f"Departure: {train_info[3]} -> Arrival: {train_info[5]}", font=("Arial", 12)).pack(pady=5)
        Label(booking_window, text=f"Price: ¥{train_info[6]}", font=("Arial", 12)).pack(pady=5)
        
        def confirm_booking():
            if not name or not id_card:
                self.utils.show_error("Error", "Please fill in all fields")
                return
                
            success, message = OrderService.create_order(
                train_info[0],  # train_number
                train_info[1],  # start_date 
                train_info[2],  # departure_station
                train_info[4],  # arrival_station
                train_info[6],  # price
                name,
                id_card
            )
            
            if success:
                self.utils.show_message("Success", message)
                booking_window.destroy()
            else:
                self.utils.show_error("Error", message)
        
        Button(booking_window, text="Confirm Booking", 
            command=confirm_booking).pack(pady=20)
        Button(booking_window, text="Cancel", 
            command=booking_window.destroy).pack(pady=5)