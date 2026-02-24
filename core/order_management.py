import tkinter as tk
from tkinter import Label, Entry, Button
from core.services import OrderService

class OrderManagementInterface:
    """订单管理界面类，处理订单查询和操作"""
    
    def __init__(self, parent_window, utils, display_table_func, show_main_menu_func):
        """初始化订单管理界面
        
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
    
    def show_order_query(self, name, id_card):
        if not name or not id_card:
            self.utils.show_error("Error", "Please fill in all fields")
            return
            
        self.display_table(
            lambda: OrderService.get_orders_by_passenger(name, id_card),
            ["order_id", "train_number", "train_type", "From", "To", 
            "Price", "customer_name", "customer_phone", "operation_type", 
            "operation_time", "status"],
            is_order_view=True,
            window_size="1200x400",
        )

    
    def cancel_order(self, order_id, refresh_callback):
        """取消订单"""
        if self.utils.show_confirmation("Confirm Cancel", "Are you sure you want to cancel this order?"):
            success, message = OrderService.cancel_order(order_id)
            if success:
                self.utils.show_message("Success", message)
                if refresh_callback:
                    refresh_callback()  # 刷新订单列表
            else:
                self.utils.show_error("Error", message)
    
    def request_refund(self, order_id, refresh_callback):
        """申请退款"""
        if self.utils.show_confirmation("Confirm Refund", "Are you sure you want to request a refund for this order?"):
            success, message = OrderService.request_refund(order_id)
            if success:
                self.utils.show_message("Success", message)
                if refresh_callback:
                    refresh_callback()  # 刷新订单列表
            else:
                self.utils.show_error("Error", message)